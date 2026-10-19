pipeline {
    agent any
    environment {
        IMAGE_NAME = 'sanskrit-bot'
        APP_DIR    = 'sanskrit-bot'
        PYTHON     = 'C:\\Users\\niran\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                bat 'git log -1 --oneline'
            }
        }
        stage('Build') {
            steps {
                dir("${APP_DIR}") {
                    bat '''
                        "%PYTHON%" -m venv .venv
                        .venv\\Scripts\\python.exe -m pip install --upgrade pip
                        .venv\\Scripts\\python.exe -m pip install -r requirements.txt
                    '''
                }
            }
        }
        stage('Test / Validate') {
            steps {
                dir("${APP_DIR}") {
                    bat '''
                        .venv\\Scripts\\python.exe -m compileall -q src app.py
                        .venv\\Scripts\\python.exe -m pytest -q --junitxml=test-results.xml
                    '''
                }
            }
            post {
                always { junit allowEmptyResults: true, testResults: "${APP_DIR}/test-results.xml" }
            }
        }
        stage('Docker Build') {
            steps {
                bat '''
                    docker build -t %IMAGE_NAME%:%BUILD_NUMBER% -t %IMAGE_NAME%:latest .
                    docker images %IMAGE_NAME%
                '''
            }
        }
        stage('Result') {
            steps {
                echo "Pipeline succeeded: ${IMAGE_NAME}:${BUILD_NUMBER} built from the latest commit."
            }
        }
    }
    post {
        failure { echo 'Pipeline FAILED. Check the stage logs above.' }
    }
}