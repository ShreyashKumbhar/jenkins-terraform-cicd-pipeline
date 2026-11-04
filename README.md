# Jenkins CI/CD + Terraform Mini Project

An end-to-end CI/CD workflow using **Jenkins** that provisions cloud infrastructure on **AWS** with **Terraform** (Infrastructure as Code). A commit pushed to GitHub is picked up by Jenkins, which checks out the code, runs unit tests, builds a deployable artifact, provisions an EC2 server with Terraform, and finally deploys and verifies the application on that server.

## 📐 Architecture

```
+------------------------+
|    Developer Commit    |
+-----------+------------+
            |
            v
+------------------------+
|   GitHub Repository    |
+-----------+------------+
            |  (SCM polling / webhook)
            v
+------------------------+
|     Jenkins Server     |
+-----------+------------+
            |
  [1. Checkout] -> [2. Unit Test] -> [3. Build] -> [4. Terraform IaC] -> [5. Deploy & Verify]
                                                          |
                                                          v
                                              +----------------------+
                                              |  AWS Infrastructure  |
                                              |  (EC2 + Sec. Group)  |
                                              +----------------------+
```

| Tool | Purpose |
| --- | --- |
| Git / GitHub | Source code repository |
| Jenkins | CI/CD automation server |
| Python (unittest) | Application and unit tests |
| Docker | Container packaging of the app |
| Terraform | Infrastructure as Code |
| AWS (EC2, Security Group) | Target cloud infrastructure |
| WSL (Ubuntu) | Linux environment for Terraform, AWS CLI and Python |

## 📁 Repository Structure

```
jenkins-terraform-cicd-pipeline/
├── Jenkinsfile              # CI/CD pipeline definition (5 stages)
├── Dockerfile               # Container packaging of the app
├── .gitignore
├── README.md
├── app/
│   ├── __init__.py
│   ├── calculator.py        # Simple calculator module (add/multiply/is_even)
│   └── index.html           # Web page deployed to the EC2 server
├── tests/
│   ├── __init__.py
│   └── test_calculator.py   # Python unit tests
└── terraform/
    ├── main.tf              # AWS provider, security group, EC2 + Nginx
    ├── variables.tf         # Configurable inputs (region, instance type, key)
    └── outputs.tf           # Server IP, security group ID, app URL
```

## 🧪 Sample Application and Tests

`app/calculator.py` contains three small functions (`add`, `multiply`, `is_even`) covered by `tests/test_calculator.py`:

```bash
python -m unittest discover -s tests -t . -v
```

The build fails if any test fails — quality gates the deployment.

## 🔧 Jenkins Pipeline Stages

| Stage | What it does |
| --- | --- |
| 1. Checkout Code | Pulls the latest code from the GitHub repository |
| 2. Lint & Unit Test | Runs the Python unit tests; the build fails if any test fails |
| 3. Build Artifact / Docker Image | Packages the app into a tarball (archived in Jenkins) and builds a Docker image when Docker is available |
| 4. Infrastructure Provisioning | Runs `terraform init`, `validate`, `plan` and `apply` to create the EC2 server and security group |
| 5. Deploy Application | Reads the server IP from Terraform outputs and verifies the application responds over HTTP |

The pipeline polls SCM every ~2 minutes (`pollSCM('H/2 * * * *')`) so any pushed commit triggers a build automatically.

## ☁️ Infrastructure as Code

`terraform/main.tf` provisions:

- A **security group** allowing SSH (22) and HTTP (80)
- An **EC2 instance** (Ubuntu 24.04 LTS, latest AMI auto-discovered) that installs Nginx via `user_data` and serves `app/index.html`

Configurable via `terraform/variables.tf`:

| Variable | Default | Description |
| --- | --- | --- |
| `aws_region` | `ap-south-1` | AWS region to deploy into |
| `instance_type` | `t3.micro` | EC2 instance type |
| `key_name` | `null` | Optional EC2 key pair for SSH access |

Outputs from `terraform/outputs.tf`: `ec2_public_ip`, `security_group_id`, `app_url`.

## 🚀 Getting Started

### Prerequisites

- [Jenkins](https://www.jenkins.io/) (with Git, Pipeline and Workspace Cleanup plugins) — job configured as **Pipeline script from SCM** pointing at this repo (`*/main`, script path `Jenkinsfile`)
- [Terraform](https://developer.hashicorp.com/terraform/downloads) ≥ 1.2 and [AWS CLI](https://aws.amazon.com/cli/) (installed in WSL Ubuntu on Windows)
- AWS credentials configured (`aws configure`) with access to EC2

### Run Terraform manually

```bash
cd terraform
terraform init       # downloads the AWS provider
terraform validate   # syntax/semantic check
terraform plan       # preview (Plan: 2 to add)
terraform apply -auto-approve    # create infrastructure
terraform destroy -auto-approve  # tear everything down to avoid charges
```

### Run the pipeline

1. Create a **Pipeline** job in Jenkins named `CI-CD-Pipeline`
2. Under **Pipeline**, choose **Pipeline script from SCM** → Git → paste the repo URL
3. Branch: `*/main`, Script Path: `Jenkinsfile`
4. Click **Save**, then **Build Now** — or just push a commit and let SCM polling trigger it

Once the pipeline finishes, the app is live at `http://<ec2_public_ip>` serving the "Deployed by Jenkins + Terraform" page.

## 💡 Why Infrastructure as Code?

Defining servers, networks and security rules in version-controlled `.tf` files instead of clicking through a cloud console makes the setup:

- **Declarative** — describe the desired end state; Terraform works out the steps
- **Repeatable** — the same files always create the same infrastructure
- **Version controlled** — infra changes tracked in Git like application code
- **Reusable** — variables let the same code run in other regions or instance sizes
- **Safe** — `terraform plan` previews every change before `apply` executes it
- **Disposable** — `terraform destroy` removes everything, avoiding leftover costs

## 🧹 Cleanup

```bash
cd terraform
terraform destroy -auto-approve
```

## 📄 License

This project is for educational purposes as part of a coursework mini project.
