This confirms the vulnerability. `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, and `webhook_id` are read straight from HTTP headers without being part of the signed payload [2](#0-1) . `HmacValidator.validate` only verifies `to_signable_string` against the app's shared `api_secret_key` [3](#0-2) , and `Registry.process` trusts `request.shop` as the tenant identifier for the handler after that check passes [4](#0-3) .

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, never from the `shop-domain` (or `topic`/`webhook-id`) header. `Utils::HmacValidator` verifies that the raw body was signed by the app's shared `api_secret_key`, but it never binds that signature to the shop the request claims to be from. `Webhooks::Registry.process` then passes the unauthenticated `shop` value straight to the app's webhook handler as the tenant identifier.

### Finding Description
The intended identity binding for a webhook should be: `shop-domain header == shop the HMAC covers`. Instead, the actual binding enforced by the gem is only `HMAC(raw_body) == valid signature over raw_body`, with `shop` entirely outside the signed scope:

- `Request#to_signable_string` returns `@raw_body` exclusively [1](#0-0) .
- `Request#shop`, `#topic`, and `#webhook_id` are read from headers with no cryptographic tie to the body or to each other [5](#0-4) .
- `HmacValidator.validate_signature` recomputes the HMAC over `to_signable_string` (the body) and compares it to the `hmac-sha256` header, with no reference to `shop` [3](#0-2) .
- `Registry.process` gates only on this body-only HMAC check, then forwards `request.shop` unchecked to `WebhookMetadata` and the registered handler [4](#0-3) .

Because Shopify signs webhooks with the app's single `client_secret` (the same secret for every shop that installs the app, not a per-shop secret), any tenant who has legitimately installed the app can capture a real, validly-signed `(raw_body, hmac)` pair delivered to them by Shopify. They can then replay that exact body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. The signature check still passes (it only covers the body), so `Registry.process` invokes the handler believing the payload originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the webhook subsystem is supposed to enforce, letting one app-installing merchant inject arbitrary webhook events (e.g., `orders/create`, `app/uninstalled`, `customers/data_request`) attributed to a different merchant's shop. Any app logic keyed off `WebhookMetadata#shop` (data sync, GDPR redaction handling, billing triggers, per-shop state machines) can be corrupted or manipulated by an unrelated party — a cross-tenant access/integrity violation, achievable without possession of the app's `client_secret` or any privileged credential.

### Likelihood Explanation
Medium-to-High: the attacker only needs to be a legitimate (even free/trial) installer of the target app to obtain one valid signed webhook body/HMAC pair, then can replay it with an arbitrary spoofed shop header at will, repeatedly, for any topic they've received.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is actually signature-checked, e.g., by verifying the header-derived shop against context established at webhook registration/session time, or by requiring the signable string to include the shop/topic alongside the body so a replay with a different shop header fails verification. At minimum, `Registry.process` should not trust `request.shop` for tenant-sensitive handling unless it has been independently corroborated (e.g., cross-checked with a known/registered shop for that specific webhook registration).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with headers including `X-Shopify-Hmac-Sha256: <validHmac>` and `X-Shopify-Shop-Domain: attacker.myshopify.com`, and some JSON body `B`.
2. Attacker resends an HTTP POST to the app's webhook endpoint with the exact same body `B` and the exact same `X-Shopify-Hmac-Sha256: <validHmac>` header, but changes `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the headers/body normally [6](#0-5) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and finds it matches, since `B` and the HMAC are unchanged [7](#0-6) .
4. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)` [8](#0-7) , causing the app to process attacker-controlled data as if it came from the victim's shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
