## Analysis

The reported bootloader bug is a class of "value trusted for identity/binding purposes is not actually covered by the authenticator that is supposed to guarantee it." Searching `lib/shopify_api/webhooks/` for the equivalent binding surfaces exactly that pattern in this gem's webhook HMAC verification.

### Root cause

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

and `ShopifyAPI::Utils::HmacValidator.validate_signature` computes/verifies the signature strictly over that signable string: [2](#0-1) 

But `topic`, `shop`, `api_version`, and `webhook_id` are all read straight from unauthenticated headers: [3](#0-2) 

`Registry.process` verifies only the body HMAC, then dispatches using the unauthenticated `topic`, and hands the unauthenticated `shop` straight to the app's handler as trusted identity: [4](#0-3) 

The binding that should hold is:
`HMAC(secret, signed_bytes) == received_hmac` implies `(shop, topic, body)` is authentic.

What actually holds is:
`HMAC(secret, raw_body) == received_hmac` implies only `body` is authentic — `shop` and `topic` are parsed but never bound into `signed_bytes`.

### Exploitability

Because `shop-domain` and `topic` sit outside the HMAC-covered bytes, anyone who can obtain a single legitimate `(raw_body, hmac)` pair from Shopify (trivially available: register a free/dev store, subscribe to any webhook topic for their own app, and capture the delivered request) can replay that exact `raw_body`+`hmac` pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (impersonating any victim shop string) and/or an arbitrary `x-shopify-topic` header (routing to a different registered handler). `Utils::HmacValidator.validate` still returns `true` because it only checks `raw_body`, and `Registry.process` forwards the forged `shop` into `WebhookMetadata` as if Shopify itself vouched for it.

This is a direct analog of the bootloader bug: a value (`EXPECTED_SYSTEM_CONTRACT_UPGRADE_TX_HASH_KEY` / here, `shop`+`topic`) is treated by downstream logic as authenticated by a check (`protocolUpgradeTxHashKey` / here, HMAC) that in fact never covers it.

### Title
Webhook `shop` and `topic` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw JSON body, so `HmacValidator.validate` authenticates the body bytes but not the `shop-domain`, `topic`, `api-version`, or `webhook-id` headers, which are parsed unauthenticated and passed on trust to the app's registered handler.

### Finding Description
`Registry.process` gates all further processing on `Utils::HmacValidator.validate(request)` [5](#0-4)  and then builds `WebhookMetadata` directly from `request.shop`, `request.topic`, `request.webhook_id`, `request.api_version` [6](#0-5) . Since the signature computed by `HmacValidator` covers only `verifiable_query.to_signable_string`, which for webhooks is exactly `@raw_body` [7](#0-6) , an attacker who has one valid `(body, hmac)` pair from Shopify (obtainable from their own store's webhook deliveries) can resend that pair with a forged `shop-domain` header naming a victim shop, and/or a forged `topic` header selecting any handler registered by the app. The check `OpenSSL.secure_compare(computed_signature, received_signature)` [8](#0-7)  still passes because the comparison never involves `shop` or `topic`.

### Impact Explanation
An app relying on `request.shop`/`WebhookMetadata#shop` to key persistence, billing, or authorization decisions (a documented, expected usage pattern, see `docs/usage/webhooks.md` guidance to construct `Request` and call `Registry.process`) will act on attacker-chosen shop identity that Shopify never actually attested to for that payload — a cross-tenant identity confusion. Combined with the unauthenticated `topic` header, an attacker can also force delivery of arbitrary captured JSON bodies into handlers for topics they were not actually generated for, corrupting business logic keyed on topic-specific body shape.

### Likelihood Explanation
Requires only that the attacker control an app installation on any Shopify store (including their own free/dev store) to legitimately receive one webhook and its valid HMAC, then replay it with modified headers to the target endpoint — no access token, `api_secret_key`, or privileged credential of the victim is needed. This is a low-effort, unprivileged-attacker path.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the bytes covered by the HMAC verification (i.e., require the app to independently verify the `shop-domain` header against a known/registered shop, and/or extend `to_signable_string` to canonically include those headers so replay/relabeling invalidates the signature), rather than authenticating body bytes alone while trusting headers implicitly.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (or any shop they control) and triggers a webhook for topic `orders/create`, capturing `raw_body` and the valid `x-shopify-hmac-sha256` header Shopify sent.
2. Attacker POSTs to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different registered `x-shopify-topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` [5](#0-4) .
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` [6](#0-5)  and processes attacker-controlled data attributed to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
