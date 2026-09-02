## Title
Webhook Shop-Domain Spoofing via HMAC Header Exclusion — Cross-Tenant Webhook Impersonation - (`lib/shopify_api/webhooks/request.rb`)

### Summary
The webhook HMAC signature verification in this gem only covers the raw request body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values — all taken from unauthenticated HTTP headers — are never included in the signed payload, yet they are trusted and forwarded directly to the app's webhook handler as the tenant identity for the event.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes the signature strictly over `verifiable_query.to_signable_string` (i.e., the body only) and compares it against the `hmac-sha256` header: [3](#0-2) 

`Registry.process` then checks only this body-HMAC before trusting the request's `shop` field and dispatching to the handler: [4](#0-3) 

Finally the untrusted `shop` header is placed directly into `WebhookMetadata`, which is the struct handed to the app's business logic as the authoritative tenant identifier: [5](#0-4) 

This breaks the intended identity binding: `hmac_valid(body) == true` should imply `shop_header == originating_shop`, but the equality the gem actually verifies is only `hmac_valid(body) == true`, independent of `shop_header`. Contrast this with the OAuth callback path, where `AuthQuery#to_signable_string` explicitly folds `shop`, `host`, `code`, `state`, and `timestamp` into the signed string, so the shop cannot be swapped without invalidating the HMAC: [6](#0-5) 

No equivalent binding exists for webhook requests.

An attacker who controls (or has installed) the same app on their own shop — a normal, unprivileged action any merchant can take — will legitimately receive webhooks with a valid `body`/`hmac-sha256` pair signed with the app's shared `api_secret_key` (a secret the attacker does not need to know, since Shopify computes it for them). Because the `shop-domain` header is excluded from the signed content, the attacker can replay that exact `body`+`hmac-sha256` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with any victim shop domain. `HmacValidator.validate` still returns `true` (the body matches), and `Registry.process` will dispatch the payload to the handler tagged with the victim's shop, letting the attacker inject events/data attributed to a shop they do not own or operate.

### Impact Explanation
This is a cross-tenant identity-binding bypass: an unprivileged actor (any merchant who can install the app) can make the gem report webhook events as originating from a different, victim tenant, causing the host application to process attacker-controlled body content under another shop's identity (e.g., triggering shop-scoped side effects such as data updates, uninstall handling, or order processing keyed on `data.shop`). This matches the Critical "cross-tenant access" impact category, since the shop identity — the tenant boundary the whole webhook system relies on — is not actually authenticated by the HMAC check.

### Likelihood Explanation
Likelihood is high for any multi-tenant app using this gem's webhook registry as documented: no access token, `client_secret`, or privileged access is required — only the ability to install the app on an attacker-controlled shop (a normal unprivileged action) to obtain one legitimate `body`/`hmac` pair, followed by a single replayed HTTP request with a modified `shop-domain` header.

### Recommendation
Include the shop domain (and ideally topic/webhook-id/api-version) in the value that is HMAC-verified, or otherwise cryptographically bind the `shop-domain` header to the signed body before trusting it as the event's tenant identity — mirroring the approach already used in `AuthQuery#to_signable_string`, which folds `shop` into the signed string. At minimum, `Registry.process` should not treat `request.shop` as authenticated unless it participated in the HMAC computation.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook topic the app subscribes to. Capture the raw request body `B` and the resulting `x-shopify-hmac-sha256` header `H` (valid because Shopify signed `B` with the shared `api_secret_key`).
2. Send a POST to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim.myshopify.com` (and any topic already registered by the app).
3. `ShopifyAPI::Webhooks::Request.new` builds successfully since required headers are present [7](#0-6) ; `HmacValidator.validate` returns `true` because only `B` is checked [8](#0-7) .
4. `Registry.process` dispatches to the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: JSON.parse(B), ...)` [9](#0-8) , causing the host app to act on attacker-supplied content as if it came from `victim.myshopify.com`.

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
