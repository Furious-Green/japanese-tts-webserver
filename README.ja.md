[English](README.md) | [日本語](README.ja.md)

# 日本語 TTS Web サーバー

複数の TTS（音声合成）モデルに対応した、FastAPI ベースの日本語 Text-to-Speech 用 Web サーバーです。

### Furious Green について

[Furious Green](https://furiousgreen.co) は、日本を拠点とする AI・機械学習・生成モデルに特化したテクノロジートレーニング企業です。本プロジェクトのようなオープンなツールやデモを公開し、エンジニアや研究者が最新の AI 技術——今回は日本語 TTS モデル——を実験・検証できる環境づくりを支援しています。

## 特長

* **複数モデル対応**：Parler TTS、Canary TTS、Fish Speech から選択可能
* **Web インターフェース**：テキスト入力と音声再生に対応したシンプルで使いやすい UI
* **日本語テキスト処理**：発音改善のための自動ルビ付与
* **リアルタイム生成**：ブラウザ上で音声を生成・再生
* **モデル比較**：モデルの切り替えが簡単で、聴き比べが容易

## 対応モデル

### Parler TTS（必須）

* **モデル**： [2121-8/japanese-parler-tts-mini](https://huggingface.co/2121-8/japanese-parler-tts-mini)
* **概要**：声質を細かく制御するために「音声説明テキスト（voice description）」を別途指定
* **VRAM**：約 2–4 GB
* **ディスク容量**：約 1–2 GB

### Canary TTS（任意）

* **モデル**： [2121-8/canary-tts-0.5b](https://huggingface.co/2121-8/canary-tts-0.5b)
* **概要**：system・user などのチャット形式プロンプトを用いた会話指向のアプローチ
* **VRAM**：約 4–6 GB
* **ディスク容量**：約 2–3 GB

### Fish Speech（任意）

* **モデル**： [OpenAudio S1](https://github.com/fishaudio/fish-speech)（API サーバー経由）
* **概要**：リファレンス音声対応のゼロショット音声クローン
* **VRAM**：最小 4 GB、推奨 12 GB
* **ディスク容量**：約 1 GB（S1-mini）または約 8 GB（S1 full）
* **特殊記法**：

  * 感情マーカー：`(angry)`, `(sad)`, `(excited)`, `(surprised)` など
  * 特殊効果：`(laughing)`, `(whispering)`, `(sighing)` など
  * 例：`こんにちは！(excited) 今日はとても良い天気ですね。(happy)`

## 必要要件

* Python 3.10 以上
* CUDA 対応 GPU（推奨。CPU でも動作しますが性能は低下）
* UV パッケージマネージャ
* **合計 VRAM**：複数モデル同時読み込み時は 12–16 GB を推奨
* **合計ディスク容量**：モデルのダウンロードとキャッシュに 5–10 GB 程度

**注意**：初回起動時に Hugging Face からモデルをダウンロードします。回線状況により 10–30 分程度かかる場合があります。

## インストール

### 1. リポジトリのクローン

```bash
git clone https://github.com/Furious-Green/japanese-tts-webserver.git
cd japanese-tts-webserver
```

### 2. 依存関係のインストール（ベース）

```bash
uv sync
```

### 3. モデル別の依存関係

#### Parler TTS（必須）

```bash
uv pip install git+https://github.com/getuka/ RubyInserter.git
uv pip install git+https://github.com/huggingface/parler-tts.git
```

#### Canary TTS（任意）

```bash
# RubyInserter は上記 Parler TTS の手順でインストール済み
uv pip install git+https://github.com/getuka/canary-tts.git
```

#### Fish Speech（任意）

Fish Speech は別途 API サーバーが必要です。以下を実施してください。

1. Fish Speech リポジトリのセットアップ

```bash
git clone https://github.com/fishaudio/fish-speech.git
cd fish-speech
# 詳細はリポジトリの README に従ってください
```

2. システム依存関係（Linux）

```bash
sudo apt install portaudio19-dev libsox-dev ffmpeg
```

3. モデルのダウンロード

```bash
# まず huggingface_hub CLI を導入
uv tool install huggingface_hub[cli]

# OpenAudio S1-mini の重みを取得
uvx --from huggingface_hub[cli] hf download fishaudio/openaudio-s1-mini --local-dir checkpoints/openaudio-s1-mini
```

4. Fish Speech API サーバーの起動

```bash
uv run --python 3.12 python -m tools.api_server \
  --listen 0.0.0.0:8080 \
  --llama-checkpoint-path "checkpoints/openaudio-s1-mini" \
  --decoder-checkpoint-path "checkpoints/openaudio-s1-mini/codec.pth" \
  --decoder-config-name modded_dac_vq
```

Web インターフェースは起動中の Fish Speech API サーバーを自動検出します。

## 使い方

### サーバー起動

```bash
# 方法 1：メインスクリプト経由
uv run python main.py

# 方法 2：uvicorn を直接使用
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Web インターフェースの操作

1. ブラウザで `http://localhost:8000` を開く
2. ドロップダウンから使用する TTS モデルを選択
3. テキストエリアに日本語テキストを入力
4. 選択モデルに応じて音声説明（voice description）などを調整
5. 「Generate Speech」を押して音声を生成・再生

## API エンドポイント

* `GET /` - Web インターフェース
* `POST /generate` - 音声生成

  * `prompt`：音声合成する日本語テキスト
  * `description`：声の特徴を表す説明テキスト
  * `model`：使用モデル（"parler" / "canary" / "fish"）
* `GET /audio/{filename}` - 生成済み音声ファイルの配信

## 設定

* **サーバーのホスト/ポート**：既定は `0.0.0.0:8000`（`main.py` で変更可能）
* **生成音声の保存先**：システムの一時ディレクトリ
* **モデルの読み込み**：初回起動時に Hugging Face から自動ダウンロード
* **GPU 利用**：CUDA が利用可能な場合は自動で GPU を使用（CPU フォールバックあり）

## 開発

### 依存パッケージの追加

```bash
uv add package-name
```

### 開発モードでの実行

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## ライセンス

MIT License — 詳細は [LICENSE](LICENSE) を参照してください。

## クレジット

本プロジェクトは以下のモデルおよびライブラリを使用しています。

* **Parler TTS** — [2121-8/japanese-parler-tts-mini](https://huggingface.co/2121-8/japanese-parler-tts-mini)
* **Canary TTS** — [2121-8/canary-tts-0.5b](https://huggingface.co/2121-8/canary-tts-0.5b)
* **Fish Speech** — [fishaudio/fish-speech](https://github.com/fishaudio/fish-speech) — OpenAudio S1 モデル
* **Ruby Inserter** — [getuka/RubyInserter](https://github.com/getuka/RubyInserter) — 日本語テキスト処理

モデル開発者およびオープンソースコミュニティの皆さまに感謝します。

## コントリビュート

貢献を歓迎します。以下の方法でご協力ください。

### 不具合報告

* まずは [Issues](https://github.com/Furious-Green/japanese-tts-webserver/issues) に同様の報告がないか確認
* 問題の内容を明確に記述
* 再現手順を記載
* 利用環境（OS / Python バージョン / GPU or CPU）を明示

### プルリクエスト

1. リポジトリをフォーク
2. 作業用ブランチを作成（例：`git checkout -b feature/amazing-feature`）
3. 変更を実装
4. 変更を十分にテスト
5. 意味のあるコミットメッセージでコミット
6. ブランチをプッシュ（`git push origin feature/amazing-feature`）
7. 変更点を説明した Pull Request を作成

### コードスタイル

* Python コードは PEP 8 に準拠
* 変数名・関数名は意味が伝わるように命名
* 複雑なロジックにはコメントを付与
* 関数は単一責務で簡潔に保つ

### 貢献いただきたい領域

* TTS モデルの追加対応
* UI/UX 改善
* パフォーマンス最適化
* ドキュメント整備
* バグ修正・エラーハンドリング強化
