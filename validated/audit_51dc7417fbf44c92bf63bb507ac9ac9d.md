### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (tenant identity), `topic`, `webhook_id`, and `api_version` fields are read from HTTP headers that are never included in the signed payload. `Webhooks::Registry.process` accepts the request as authentic once the body-only HMAC matches, then forwards the unauthenticated `shop` header value straight to the host application's handler as `WebhookMetadata#shop`. This breaks the intended binding `HMAC-verified bytes == bytes acted upon`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all derived from headers that are outside that signable string: [2](#0-1) 

`Utils::HmacValidator.validate_signature` verifies the HMAC strictly against `to_signable_string` (i.e., the raw body), never the headers: [3](#0-2) 

`Webhooks::Registry.process` treats a passing HMAC check as proof the entire request — including the `shop` header — is authentic, then immediately hands the unauthenticated `request.shop` to the developer-supplied handler: [4](#0-3) 

The resulting `WebhookMetadata#shop` field is a plain, unauthenticated string that host applications are expected to trust as the tenant identity for the event: [5](#0-4) 

This differs from `Auth::Oauth::AuthQuery`, where `shop` and `host` are explicitly folded into `to_signable_string` and thus are bound by the HMAC: [6](#0-5) 

Because the webhook HMAC only proves "this body byte-string was produced with the app's secret at some point," and says nothing about which shop, topic, or webhook id it was originally emitted for, an attacker who can obtain **any one legitimate, valid webhook delivery** (e.g., from their own connected shop — no secret or privileged access required) can capture the `(raw_body, X-Shopify-Hmac-Sha256)` pair and replay it to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop's domain (and optionally a different topic/webhook-id/api-version). `HmacValidator.validate` will still return `true`, because it never inspects those headers, so `Registry.process` will call the handler with `WebhookMetadata.new(shop: "<victim-shop>", ...)` alongside the attacker-supplied body.

### Impact Explanation
This is a cross-tenant identity confusion: the equality the gem is supposed to guarantee, `hmac_verified_bytes == identity_used_by_handler`, does not hold, since `shop` (and `topic`/`webhook_id`) sit entirely outside the signed bytes. Any host application that uses `data.shop` from `WebhookMetadata` to select which merchant's record to update, credit, uninstall, or otherwise mutate — which is the standard, documented usage pattern shown in `docs/usage/webhooks.md` — can be tricked into applying an attacker-controlled payload under a victim shop's identity. Depending on the handler's logic (e.g., `app/uninstalled`, `shop/redact`, billing-related topics), this can lead to cross-tenant data corruption or unauthorized state changes attributed to a shop the attacker does not control, without needing the app's `client_secret`, access token, or any privileged credential — only a single previously-observed legitimate webhook body+hmac pair.

### Likelihood Explanation
Any merchant who installs the app (a normal unprivileged action) legitimately receives valid webhook deliveries for their own shop and can trivially capture `raw_body` and the `X-Shopify-Hmac-Sha256` header for a webhook of their choosing (e.g., by triggering `orders/create` with attacker-controlled order content). Replaying that exact body with a forged `X-Shopify-Shop-Domain`/`X-Shopify-Topic`/`X-Shopify-Webhook-Id` header to the app's public webhook endpoint requires no secret material at all, since `HmacValidator` never checks these headers. This makes the attack straightforward for anyone who can install the app on a store they control.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or otherwise cryptographically bind them to the raw body before verification (e.g., verify `HMAC(secret, shop + "|" + topic + "|" + webhook_id + "|" + raw_body)`), so that `Utils::HmacValidator.validate` fails if any of these headers are altered relative to the originally signed webhook. At minimum, document that `WebhookMetadata#shop`/`#topic`/`#webhook_id` are unauthenticated and must be independently cross-checked against the app's known-shop/session store before being trusted, and consider adding this cross-check inside `Webhooks::Registry.process` itself.

### Proof of Concept
```ruby
# Step 1: attacker (owner of "attacker-shop.myshopify.com") captures a legitimate delivery
raw_body = '{"id":1,"note":"hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret, raw_body)
# headers actually received by the app for the attacker's own shop:
# x-shopify-topic: orders/create
# x-shopify-hmac-sha256: Base64.encode64(hmac)
# x-shopify-shop-domain: attacker-shop.myshopify.com

# Step 2: attacker replays the identical body/hmac but swaps the shop header
forged_headers = {
  "x-shopify-topic"        => "orders/create",
  "x-shopify-hmac-sha256"  => Base64.encode64(hmac), # unchanged, still valid because HMAC only covers raw_body
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # forged
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) => true, because it only checks raw_body
# The registered handler is invoked with WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
```
As shown, `Utils::HmacValidator.validate` at [7](#0-6)  accepts the forged request unchanged, and `Registry.process` at [4](#0-3)  dispatches it to the handler with the attacker-chosen `shop` value.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
