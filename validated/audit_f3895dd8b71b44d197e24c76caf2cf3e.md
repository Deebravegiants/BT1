### Title
Webhook shop identity and topic are trusted from unauthenticated headers while the HMAC only covers the raw body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as verified once `Utils::HmacValidator.validate(request)` passes, and then hands `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to the app's handler as trustworthy tenant-identifying data. But the HMAC signature only ever covers the raw request body — the shop domain, topic, webhook id and API version are read straight from HTTP headers that are completely outside the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns `@raw_body` only [1](#0-0) , and `hmac`, `topic`, `shop`, `api_version`, and `webhook_id` are all pulled independently from HTTP headers via `shopify_header` [2](#0-1) . `HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` (the body) and compares it to the `hmac` header [3](#0-2) . `Registry.process` gates entirely on this HMAC check and then constructs `WebhookMetadata` directly from `request.shop`, `request.topic`, `request.webhook_id`, `request.api_version` [4](#0-3) , none of which are part of the signed bytes.

This breaks the intended identity binding: `shop-header-that-is-trusted == shop-bytes-that-are-HMAC-verified`. In reality the equality only holds for `raw_body-bytes-verified == raw_body-bytes-signed`; the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are never bound to the signature at all. This is the same root-cause pattern as the referenced report's "bytes verified versus bytes parsed" class: the gem verifies one set of bytes (the body) but acts on a different, unauthenticated set of bytes (the headers) as if they had passed the same integrity check.

The gem's own documentation reinforces the false assumption, stating that calling `Registry.process` "will verify the request did indeed come from Shopify" without qualifying that only the body — not the shop, topic, or webhook id — is actually verified [5](#0-4) .

### Impact Explanation
Because the `api_secret_key` is shared across all merchants installing a given app, any party who can obtain one legitimately-signed webhook body/HMAC pair (e.g., by installing the app on their own test/attacker-controlled shop and capturing a real webhook delivery) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) header. The HMAC check still passes because it only validates the body bytes, so `Registry.process` will happily dispatch the handler with `WebhookMetadata#shop` set to a victim shop the attacker never had access to. Any host application that uses `data.shop` from `WebhookMetadata` as the tenant key (exactly as shown in the gem's own usage example) will process attacker-controlled body content under a different, victim tenant's identity — a cross-tenant data injection/impersonation without any of the victim's credentials.

### Likelihood Explanation
Exploitation only requires network access to the app's public webhook endpoint and one previously-observed valid (body, HMAC) pair from any shop using the same app installation — no access token, `client_secret`, or privileged account is needed, satisfying the unprivileged-internet-user bar. This is a straightforward header-substitution replay, not a cryptographic break.

### Recommendation
Bind the shop/topic/webhook identity into the verified signature surface, or otherwise fail closed when the header-derived shop cannot be corroborated: e.g., include the `shop-domain`/`topic`/`webhook-id` headers in `to_signable_string` (with per-field escaping) so they participate in the HMAC, or require the caller/host app to independently confirm the header-derived shop against a known/registered session before trusting `WebhookMetadata#shop`. At minimum, update the documentation to clarify that `Registry.process` verifies body integrity only and that shop/topic/webhook_id are unauthenticated.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and lets Shopify deliver a real webhook, capturing the raw body `B` and its valid `x-shopify-hmac-sha256` header `H` (computed by Shopify using the app's shared `api_secret_key`).
2. Attacker POSTs to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com` and any desired `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers [6](#0-5) ; `HmacValidator.validate` succeeds because it only re-hashes `B` [7](#0-6) .
4. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` [4](#0-3) , and any host application that keys its side effects off `data.shop` (per the documented usage pattern) performs them under the victim's tenant identity using attacker-controlled body content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L11-33)
```ruby
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
