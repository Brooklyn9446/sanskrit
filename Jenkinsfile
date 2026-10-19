pipeline {
    agent any
    environment {
        IMAGE_NAME = 'sanskrit-bot'
        APP_DIR    = 'sanskrit-bot'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }
        stage('Build') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        python3 -m venv .venv
                        . .venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        stage('Test / Validate') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        . .venv/bin/activate
                        python -m compileall -q src app.py
                        pytest -q --junitxml=test-results.xml
                    '''
                }
            }
            post {
                always { junit "${APP_DIR}/test-results.xml" }
            }
        }
        stage('Docker Build') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest .
                    docker images ${IMAGE_NAME}
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