# 概要

当リポジトリは、DJI Cloud API対応の無人航空機と接続し、テレメトリ情報を変換し、外部システムに送信するアプリケーションの実装例を、OSSとして公開したものである。

### アプリケーション構成

当アプリケーションは、DJI CloudAPIおよび外部システム連携(dji-cloud-api-to-utm)で構成される。
本リポジトリでは dji-cloud-api-to-utm を説明対象とする。
外部システム連携については、フレームワーク、共通機能、Cloud APIとの接続、および外部システムとの接続部分を除き、テレメトリ情報変換部分のみを提供する。

![アプリケーション概要図](docs/img/overview.PNG)

## 前提とする環境
### 必要となる外部アプリケーション
 [DJI公式サイト](https://developer.dji.com/doc/cloud-api-tutorial/en/)で公開されている、DJI CloudAPIのsampleアプリ
 開発環境をインストールしたくない場合は、docker を使用してデプロイしてみてください。 [Click the link to download.](https://terra-sz-hc1pro-cloudapi.oss-cn-shenzhen.aliyuncs.com/c0af9fe0d7eb4f35a8fe5b695e4d0b96/docker/cloud_api_sample_docker.zip)

### アプリケーション実行環境

| ツール    | バージョン |
| --------  | ---------  |
| python    |  3.13.0    |
| protobuf  |  5.28.3    |
| redis     |  5.2.0     |
| paho-mqtt |  2.1.0     |

## 問合せ及び要望に関して

- 本リポジトリは現状は主に配布目的の運用となるため、IssueやPull Requestに関しては受け付けておりません。

## ライセンス

- 本リポジトリはMITライセンスで提供されています。
- ソースコードおよび関連ドキュメントの著作権は株式会社NTTデータに帰属します。

## 免責事項

- 本リポジトリの内容は予告なく変更・削除する可能性があります。
- 本リポジトリの利用により生じた損失及び損害等について、いかなる責任も負わないものとします。

## 更新履歴

- テレメトリ変換処理にミッション中のホバリング状態(`INFLIGHT_MISSION_HOVER`)を追加しました。

