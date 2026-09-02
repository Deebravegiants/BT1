## Finding [1](#0-0) 

The reported bug class ("field acted on but not covered by the cryptographic check") maps directly onto how Shopify webhooks are authenticated in this gem: the `Shopify-Shop-Domain` header is trusted as the tenant identity, but the HMAC only covers the raw body.

### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `ShopifyAPI::Utils::HmacValidator.validate` computes/verifies the HMAC exclusively over that string. [2](#0-1) [3](#0-2) 
The `shop` value dispatched to the app's handler, however, is read straight from the `Shopify-Shop-Domain`/`X-Shopify-Shop-Domain` header, which is never included in the signed material. [4](#0-3) 
`ShopifyAPI::Webhooks::Registry.process` validates only the body HMAC and then forwards `request.shop` (the unauthenticated header) straight to the handler as the tenant identity. [5](#0-4) 

### Finding Description
The identity binding that should hold is:
`shop asserted in WebhookMetadata.shop == shop that produced/authorizes the HMAC-signed body`.

In this gem's webhook flow, the HMAC secret (`Context.api_secret_key`) is the app's single, global client secret — it is **not** shop-specific. Therefore:
- Any body byte-string that is validly HMAC'd with the app secret will pass `HmacValidator.validate`, regardless of which shop it was originally sent for.
- The `shop` field attached to the resulting `WebhookMetadata` (and used by host-app handlers to key database writes, authorization decisions, etc.) comes from a header that is completely outside the HMAC's coverage.

Because the header is never bound to the signature, an entity that can produce or capture one validly-signed webhook body/HMAC pair (e.g., a merchant who has installed the app, and thus legitimately receives HMAC'd webhooks for their own shop) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header for a *different* shop that also uses the app. `Utils::HmacValidator.validate` will still return `true` because it only checks the raw body against the shared secret, and `Registry.process` will dispatch to the handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop domain.

### Impact Explanation
This breaks the tenant isolation the host application relies on: the gem asserts a shop identity to downstream handler code without any cryptographic guarantee that the signed payload actually originated for that shop. A downstream app that trusts `data.shop` (as the documented API contract implies) to scope database updates/uninstall processing/etc. can be tricked into applying attacker-supplied webhook data under another merchant's identity — a cross-tenant data-integrity/confidentiality issue reachable purely through the gem's own webhook-processing surface, with no need for the app's `client_secret` or an access token.

### Likelihood Explanation
Exploitation requires the attacker to control (or have previously observed) one genuine HMAC-body/webhook pair from their own legitimately-installed instance of the app — a low bar for any merchant/dev-store owner who installs the target app — and to be able to POST directly to the app's public webhook endpoint with a forged shop header, which the gem's `Request` parser accepts without validating that the header's shop matches the body's origin.

### Recommendation
Bind the tenant identity into the value that's cryptographically checked, e.g. verify the claimed `shop` against a previously-registered/known-good shop record (or against the session/shop mapping the app already trusts) before dispatching the webhook, rather than trusting the header at face value once the *body* HMAC passes. At minimum, `Registry.process` (or `HmacValidator`) should be extended so the "shop" identity can't be swapped independently of the signed payload it's associated with.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, receives a normal webhook with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac of body>` and some `raw_body`.
2. Attacker POSTs the identical `raw_body` and `X-Shopify-Hmac-Sha256` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this successfully (headers are all present, format valid). [6](#0-5) 
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the raw body against the app's global secret (same secret for all shops, including the attacker's own shop and the victim's shop). [5](#0-4) 
5. The registered handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, causing the host app to process attacker-controlled webhook data as if it legitimately originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
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
