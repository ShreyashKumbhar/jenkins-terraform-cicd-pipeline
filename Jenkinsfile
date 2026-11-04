
pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-south-1'
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    stages {

        stage('1. Checkout Code') {
            steps {
                echo 'Checking out source code from GitHub...'
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('2. Lint & Unit Test') {
            steps {
                echo 'Running unit tests...'
                sh 'python3 -m unittest discover -s tests -t . -v'
            }
        }

        stage('3. Build Artifact / Docker Image') {
            steps {
                echo 'Packaging application...'
                sh 'tar -czf app-build.tar.gz app Dockerfile'

                sh '''
                    if docker info >/dev/null 2>&1; then
                        docker build -t cicd-demo-app:${BUILD_NUMBER} .
                    else
                        echo "Docker not available - image build skipped"
                    fi
                '''

                archiveArtifacts artifacts: 'app-build.tar.gz', fingerprint: true
            }
        }

        stage('4. Infrastructure Provisioning (Terraform)') {
            steps {
                dir('terraform') {
                    echo 'Provisioning AWS infrastructure with Terraform...'
                    sh 'terraform init -input=false'
                    sh 'terraform validate'
                    sh 'terraform plan -input=false -out=tfplan'
                    sh 'terraform apply -input=false -auto-approve tfplan'
                }
            }
        }

        stage('5. Deploy Application') {
            steps {
                dir('terraform') {
                    script {
                        def ip = sh(
                            returnStdout: true,
                            script: 'terraform output -raw ec2_public_ip'
                        ).trim()

                        echo "Application server IP: ${ip}"
                        echo 'Waiting for Nginx and verifying deployment...'

                        retry(10) {
                            sleep 20
                            sh "curl -sf http://${ip}"
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
