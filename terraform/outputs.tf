output "ec2_public_ip" {
  description = "Public IP of the provisioned EC2 instance"
  value       = aws_instance.app_server.public_ip
}

output "security_group_id" {
  description = "ID of the created security group"
  value       = aws_security_group.jenkins_app_sg.id
}

output "app_url" {
  description = "URL of the deployed application"
  value       = "http://${aws_instance.app_server.public_ip}"
}
