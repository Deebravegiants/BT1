## Analysis

The report's "missing bound tied to identity/authorization" pattern maps cleanly onto how `ShopifyAPI::Webhooks::Request` computes what is HMAC-protected versus what a webhook handler trusts as tenant identity.

### The binding that should hold
`HMAC-SHA256(api_secret_key, signed_bytes)` should authenticate **all** fields the handler uses to attribute a webhook to a tenant. Concretely: `shop` used for tenant routing == `shop` covered by the verified signature.

### What the code actually does

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from unauthenticated HTTP headers, none of which feed into `to_signable_string`: [2](#0-1) 

`Registry.process` validates only the body HMAC, then builds tenant-attributed metadata directly from those unsigned headers and dispatches it to the app's handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever compares `verifiable_query.to_signable_string` (the raw body, in the webhook case) against the HMAC — it has no knowledge of `shop`, `topic`, or `webhook_id`: [4](#0-3) 

Contrast this with `Auth::Oauth::AuthQuery`, where `shop` **is** included in the signed payload, so the equivalent binding does hold for OAuth callbacks: [5](#0-4) 

### Exploitability

Because the webhook secret (`api_secret_key`) is shared across all shops that install the app, an attacker who controls any shop where the app is installed can:
1. Trigger a legitimate webhook from their own store (any topic/body they can influence) — Shopify signs it with the app's real `api_secret_key` over the raw body only.
2. Replay that exact `raw_body` + `X-Shopify-Hmac-Sha256` value to the app's public webhook endpoint, substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain.
3. `HmacValidator.validate` still succeeds (same secret, same body — headers are irrelevant to the check), and `Registry.process` forwards `WebhookMetadata` with `shop:` set to the attacker-chosen victim domain to the app's handler.

This lets a single-tenant attacker inject data/events that the host application will process and persist as if they originated from a different tenant — a cross-tenant confusion that this gem's webhook API enables by not binding `shop` (or `topic`/`webhook_id`) to the signature it verifies.

### Title
Webhook shop/topic/webhook-id headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw body via `to_signable_string`, while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated headers and passed straight into `WebhookMetadata` after `Registry.process` confirms only the body's HMAC. Any party able to obtain one valid `(raw_body, hmac)` pair for the shared app secret (e.g., by installing the app on their own shop) can replay it with a forged `Shop-Domain` header to make the app attribute attacker-controlled webhook data to an arbitrary victim shop.

### Finding Description
The gem's webhook signature check (`HmacValidator.validate` → `validate_signature`) computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` accessor. For `Webhooks::Request`, `to_signable_string` returns `@raw_body` only [1](#0-0) , but `shop`, `topic`, and `webhook_id` are exposed as separate accessors sourced from headers that are never included in the signed bytes [2](#0-1) . `Registry.process` trusts these header-derived values to build `WebhookMetadata` for the handler after only checking the body HMAC [3](#0-2) . The identity binding "shop verified by the HMAC" ≠ "shop used by the handler" is broken.

### Impact Explanation
This allows cross-tenant webhook spoofing: a party that can obtain any one valid signed body for the shared `api_secret_key` (trivially, by having the app installed on their own store and capturing their own genuine webhook) can relabel it as coming from any other shop. The host app's webhook handler — which typically uses `shop` to select the tenant's DB record/session to act on — will process/store attacker-controlled data under the victim tenant's identity, which is a cross-tenant access impact.

### Likelihood Explanation
Requires only the ability to receive one legitimate webhook for a shop where the app is installed (any developer/merchant installing the app satisfies this) and the ability to POST to the app's public webhook endpoint with a custom `Shop-Domain` header — no access token, `api_secret_key`, or privileged credentials needed.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signed material (or otherwise cryptographically bind them to the signed body), or require applications to cross-check `request.shop` against a shop already known/authorized for that specific webhook subscription rather than trusting the header value once the body HMAC passes.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook subscription so Shopify sends `POST /webhooks` with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac of raw body>`, and some `raw_body`.
2. Capture `raw_body` and the `hmac` value.
3. Replay: `POST /webhooks` with identical `raw_body` and `X-Shopify-Hmac-Sha256`, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds because it only checks the body. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) dispatches `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker-controlled>)` to the app's handler, which acts on victim's tenant data using attacker-supplied content.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
