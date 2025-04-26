# Backend Service Deployment (AWS CDK + Python)

## 📆 Project Overview

This project contains the AWS CDK infrastructure code for deploying a backend system on AWS, consisting of two containerized services:
- **Product Service**
- **Order Service**

The infrastructure is fully deployed using AWS CDK in Python, and runs in an AWS VPC with an Application Load Balancer (ALB) distributing traffic to ECS Fargate containers.

---

## 🚀 Setup Guide

Follow these steps to set up and deploy the backend services.

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/backend-service.git
cd backend-service
```

---

### 2. Create a Python Virtual Environment

Create a virtual environment to isolate project dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate  # For Mac/Linux
```

---

### 3. Install Python Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

Main dependencies:
- `aws-cdk-lib`
- `constructs`

---

### 4. Install AWS CDK CLI (If not installed)

Install AWS CDK globally:

```bash
npm install -g aws-cdk
```

Check CDK version:

```bash
cdk --version
```
(Recommended: CDK v2.x or above)

---

### 5. Configure AWS Credentials

Configure your AWS credentials locally:

```bash
aws configure
```

Input:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)
- Default output format (press Enter for none)

---

### 6. Bootstrap AWS Environment (Required Once)

Prepare your AWS account to use CDK:

```bash
cdk bootstrap aws://<your-aws-account-id>/<your-region>
```

Example:

```bash
cdk bootstrap aws://123456789012/us-east-1
```

---

### 7. Synthesize CloudFormation Template

Generate the CloudFormation template locally:

```bash
cdk synth
```

This prepares the deployment plan based on your code.

---

### 8. Deploy to AWS

Deploy your backend services:

```bash
cdk deploy
```

This will provision:
- VPC (Virtual Private Cloud)
- ALB (Application Load Balancer)
- ECS Cluster
- Two Fargate container services (Product & Order)

---

## 📄 Project Structure

```plaintext
backend-service/
├── app.py                 # CDK stack entry point
├── cdk.json                # CDK app configuration
├── requirements.txt        # Python dependencies
├── README.md               # Project setup guide
├── .gitignore              # Git ignore settings
└── cdk.out/                # Generated CloudFormation templates
```

---

## 📢 Notes

- Make sure your IAM user has `AdministratorAccess` permission.
- After modifying `app.py` or any CDK code, rerun:
  ```bash
  cdk synth
  cdk deploy
  ```
- After updating Python dependencies, refresh your `requirements.txt`:
  ```bash
  pip freeze > requirements.txt
  ```
- Use `cdk destroy` to remove all AWS resources created by this deployment if needed:
  ```bash
  cdk destroy
  ```

---

## ✨ About

This project demonstrates a scalable backend infrastructure on AWS using AWS CDK, ECS Fargate, and ALB, designed for cloud-native deployment best practices.

