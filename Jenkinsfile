//Jenkinsfile (Declarative Pipeline)
pipeline{
    agent{
        label '003Builder_225'
    }
	environment{
		tools_path="003Scripts"
		/*gitlabSourceNamespace="SCWB300"
        gitlabSourceRepoName="PSCD"
        gitlabBranch="ALAE_release"
        gitlabUserEmail="wangkk"*/
    }
    stages{
        stage('get clone'){
			steps{
				script{
					component="$gitlabBranch".split("_")[0]
                }
				checkout([$class: 'GitSCM', branches: [[name: "*/$gitlabBranch"]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'WipeWorkspace'], [$class: 'CleanBeforeCheckout']], submoduleCfg: [], userRemoteConfigs: [[credentialsId: '924f7cae-d453-421c-a074-4467480086f0', url: '$gitlabSourceRepoHttpUrl']]])
				script{
					ret=fileExists component
					if(!ret){
						bat 'dir'
						error 'δ�ҵ�Ŀ¼'+component
					}
                }
			}
		}
		stage("copy tools"){
			steps{
				dir("../__$tools_path") {
					git branch: 'dev', credentialsId: '924f7cae-d453-421c-a074-4467480086f0', url: 'http://172.16.20.118:8000/SCWB300/Builder.git'
					bat "xcopy $tools_path $WORKSPACE\\$component\\$tools_path /s /e /y /i"
				}
			}
		}
		stage('start'){
			steps{
				dir(component) {
					bat 'dir'
					withSonarQubeEnv('sonarqube'){
						bat "python $tools_path/003Script.py $gitlabSourceNamespace $gitlabSourceRepoName $gitlabBranch"
					}
					bat 'dir'
					script{
						if("$gitlabBranch".indexOf("release")!=-1){
							def qg=waitForQualityGate()
							if(qg.status!="OK"){
								echo "Sonarqube�����ⲻ�ϸ�"
								emailext body: "<hr/>(���ʼ���Jenkins�Զ��·�������ظ���)<br/><hr/>��Ŀ���ƣ�$gitlabSourceNamespace<br/><hr/>�����Ϣ��$gitlabSourceRepoName - $gitlabBranch <br/><hr/>������־��ַ��<a href="+"${BUILD_URL}console"+">Jenkins</a><br/><hr/>Sonaqube��ַ��<a href="+"http://172.16.42.225:9000/dashboard?id=${gitlabSourceNamespace}_${gitlabSourceRepoName}_${gitlabBranch}"+">Sonarqube</a><br/><hr/>", 
								subject: "Jenkins����֪ͨ��Sonarqube�����ⲻ�ϸ�", 
								to: "$gitlabUserEmail"
							}
						}
					}
				}
			}
		}
    }
    post{
		failure{
			emailext body: "<hr/>(���ʼ���Jenkins�Զ��·��ģ�����ظ���)<br/><hr/>��Ŀ���ƣ�$gitlabSourceNamespace<br/><hr/>�����Ϣ��$gitlabSourceRepoName - $gitlabBranch <br/><hr/>������ţ�$currentBuild.number<br/><hr/>����״̬��$currentBuild.currentResult<br/><hr/>������־��ַ��<a href="+"${BUILD_URL}console"+">Jenkins</a><br/><hr/>", 
			subject: "Jenkins����֪ͨ:$gitlabSourceNamespace - $gitlabSourceRepoName($gitlabBranch) Build # $BUILD_NUMBER - $currentBuild.currentResult", 
			to: '$gitlabUserEmail,wangkk@smee.com.cn'
		}
		always{
			cleanWs()
		}
	}
}