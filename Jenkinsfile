pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-south-1'
    }

    triggers {
        pollSCM('H/2 * * * *')   // check GitHub for new commits every ~2 minutes
    }

    stages {

        stage('1. Checkout Code') {
            steps {
                echo 'Checking out source code from GitHub...'
                checkout scm
                bat 'git log -1 --oneline'
            }
        }

        stage('2. Lint & Unit Test') {
            steps {
                echo 'Running unit tests...'
                bat 'wsl python3 -m unittest discover -s tests -t . -v'
            }
        }

        stage('3. Build Artifact / Docker Image') {
            steps {
                echo 'Packaging application...'
                bat 'wsl tar -czf app-build.tar.gz app Dockerfile'
                bat 'wsl sh -c "docker info >/dev/null 2>&1 && docker build -t cicd-demo-app:%BUILD_NUMBER% . || echo Docker not available - image build skipped"'
                archiveArtifacts artifacts: 'app-build.tar.gz', fingerprint: true
            }
        }

        stage('4. Infrastructure Provisioning (Terraform)') {
            steps {
                dir('terraform') {
                    echo 'Provisioning AWS infrastructure with Terraform inside WSL...'
                    bat 'wsl terraform init -input=false'
                    bat 'wsl terraform validate'
                    bat 'wsl terraform plan -input=false -out=tfplan'
                    bat 'wsl terraform apply -input=false -auto-approve tfplan'
                }
            }
        }

        stage('5. Deploy Application') {
            steps {
                dir('terraform') {
                    script {
                        def ip = bat(returnStdout: true, script: '@wsl terraform output -raw ec2_public_ip').trim()
                        echo "Application server IP: ${ip}"
                        echo 'Waiting for Nginx on the new server and verifying deployment...'
                        retry(10) {
                            sleep 20
                            bat "wsl curl -sf http://${ip}"
                        }
                        echo "Application is live at http://${ip}"
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution complete.'
        }
        success {
            echo 'CI/CD Pipeline succeeded!'
        }
        failure {
            echo 'CI/CD Pipeline failed. Please check build logs.'
        }
    }
}
