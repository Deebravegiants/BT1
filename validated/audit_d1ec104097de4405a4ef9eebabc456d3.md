This confirms the finding. The docs explicitly document `data.shop` (line 14 of `docs/usage/webhooks.md`) as "The shop domain of the webhook" and shows a canonical usage pattern where the shop domain is trusted directly to route/attribute per-tenant work (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), yet nothing in `ShopifyAPI::Webhooks::Request` or `ShopifyAPI::Webhooks::Registry.process` binds that `shop` field to the HMAC signature.

### Title
Webhook shop-domain header not covered by HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only that HMAC before dispatching `request.shop` to the app's handler as the trusted tenant identity.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes and compares an HMAC over `verifiable_query.to_signable_string`. For webhook requests, `to_signable_string` is defined as: [1](#0-0) 

which returns only `@raw_body`. The `shop`, `topic`, `webhook_id`, and `api_version` values are pulled from HTTP headers that are never part of the signed content: [2](#0-1) 

`Registry.process` then validates only the HMAC of the body and immediately trusts `request.shop` as the tenant identity handed to the app's handler: [3](#0-2) 

The equality the HMAC is supposed to guarantee is: `hmac_valid(body, secret) == true` implies `(body, shop) is the message Shopify signed for that shop`. In reality it only guarantees body integrity: `hmac_valid(body) == true` implies `body was produced by an entity holding api_secret_key`, with **no** binding between that secret-holder and the `shop` header value. Since `api_secret_key` is shared across *all* shops that install the app (it's the app's own client secret, not a per-shop secret), any merchant who has legitimately installed the app on their own store can capture a real webhook delivery — with a valid HMAC over the body — and replay the identical body+HMAC to the app's webhook endpoint while substituting an arbitrary value in the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header. `HmacValidator.validate` passes because it never inspects that header, and `Registry.process` forwards the spoofed `shop` value straight to the handler as `WebhookMetadata#shop`, which the docs explicitly instruct developers to trust as "The shop domain of the webhook" for tenant-scoped processing.

### Impact Explanation
This breaks the tenant/shop authentication boundary that host applications rely on to scope webhook side effects (e.g., updating per-shop settings, disabling features, recording orders/refunds, deleting data for GDPR topics) to the correct tenant. An attacker with any legitimate install of the target app (even a free/dev store) can forge webhooks that appear to originate from a victim shop, causing the host application to perform actions or store attacker-controlled data under the victim shop's identity — a cross-tenant access/data-integrity violation. This matches the "cross-tenant access" Critical-impact category, since no additional secret or session state beyond a valid own-tenant webhook is required.

### Likelihood Explanation
Likelihood is high for any app relying on this gem's webhook helpers exactly as documented: an attacker only needs to install the target app on any shop they control (which requires no special privilege — apps in the Shopify App Store or custom-distributed apps can typically be installed on trial/dev stores), capture one webhook delivery, and replay it with a modified `shop` header to the app's public webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the HMAC-covered signable string, or otherwise verify that the `shop` header matches a shop associated with a valid, previously issued session/access token before trusting it in `WebhookMetadata`. At minimum, document prominently that `data.shop` from `ShopifyAPI::Webhooks::Request` is **not** cryptographically bound to the signature and must be independently reconciled against known installed shops before being used for tenant-scoped actions.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a store they control).
2. Attacker triggers a webhook (e.g., `orders/create`) and captures the raw POST body and its `X-Shopify-Hmac-Sha256` header — this HMAC is valid because it's computed with the app's shared `api_secret_key`, per [4](#0-3) .
3. Attacker replays the exact same body and HMAC header to the app's public webhook endpoint, but changes the `X-Shopify-Shop-Domain` header to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (only checks header presence, not shop correctness): [5](#0-4) 
5. `Registry.process` validates the HMAC (over body only, passes) and invokes the handler with `shop: request.shop` set to `victim-shop.myshopify.com`: [3](#0-2) 
6. The host application's webhook handler (following the documented pattern in `docs/usage/webhooks.md` lines 24-27, which calls `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) performs shop-scoped work attributing the attacker's forged data to the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
