### Title
Webhook shop-domain identity is trusted from an unauthenticated header while the HMAC binds only the raw body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` derive the HMAC verification value exclusively from `@raw_body`, while the tenant-identifying `shop-domain` header is read separately via `shopify_header("shop-domain")` and is never included in the signed material. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC against the body only and then forwards `request.shop` straight into `WebhookMetadata`, which host applications use to identify the tenant the webhook belongs to. This breaks the intended identity binding: `HMAC(secret, signed_bytes) == received_hmac` should imply `shop == the shop that produced signed_bytes`, but here `signed_bytes` (the body) and `shop` are independent, unauthenticated-relative-to-each-other fields.

### Finding Description
The equality the gem is supposed to guarantee for every processed webhook is:

`valid_hmac(raw_body, api_secret_key) ⟺ (raw_body, shop) originated together from Shopify for that shop`

What is actually checked:

- `to_signable_string` returns only `@raw_body` [1](#0-0) 
- `hmac` is read from the `hmac-sha256` header [2](#0-1) 
- `shop` is read from a completely separate `shop-domain` header, with no cryptographic relationship to the body or the HMAC [3](#0-2) 
- `HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it only against the received `hmac`, so it validates the body alone [4](#0-3) 
- `Registry.process` performs exactly this check and then unconditionally trusts `request.shop` for tenant attribution [5](#0-4) 

Because the app's `client_secret`/`api_secret_key` is shared across every shop that installs the app (it is not per-shop), any entity that can obtain one valid `(raw_body, hmac)` pair for a webhook delivered to their own shop — which requires nothing more than installing the app on any store, something an unprivileged internet user can do — can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary value in the `shop-domain` header. The HMAC still validates because it never covered the header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to a shop the attacker does not control.

### Impact Explanation
This is a cross-tenant identity-binding break: the gem authenticates the payload's integrity but not the tenant it is attributed to, then lets the unauthenticated tenant field flow into application logic (`WebhookMetadata#shop`, documented as "The shop domain of the webhook"). Host applications built on this gem's documented contract — that a webhook passing `Registry.process` is a verified message "from Shopify" for the stated `shop` — will process attacker-controlled body content under another tenant's identity (e.g., writing customer/order/GDPR data or triggering per-shop side effects keyed by `data.shop`), which is a cross-tenant access impact reachable purely through this gem's own verification code.

### Likelihood Explanation
Requires only: (1) installing the app on an attacker-controlled/dev store to legitimately receive one signed webhook (no privileged credentials, no access token theft, no TLS interception — normal app installation), and (2) POSTing the captured body+HMAC to the app's public webhook route with a forged `shop-domain` (or `x-shopify-shop-domain`) header. Both are within reach of an unprivileged internet user and do not depend on the host app deviating from the gem's documented usage (`docs/usage/webhooks.md` shows the exact pass-through pattern of `data.shop`).

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically tie the `shop-domain` header to the verified payload, e.g. include the shop domain (and ideally topic/webhook-id) in `to_signable_string`, or require the caller to independently corroborate `shop` against a per-shop secret/session lookup rather than trusting the header verbatim. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be used for tenant-sensitive decisions without further verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and lets Shopify deliver one real webhook, capturing `raw_body` and the `X-Shopify-Hmac-Sha256` header value.
2. Attacker sends a POST to the app's webhook endpoint with the identical `raw_body`, the identical `hmac-sha256` header, but `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present) [6](#0-5) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, raw_body)` and compares to the unmodified header — it matches because the body wasn't changed [7](#0-6) .
5. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's original payload>, ...)` [8](#0-7) , and the host app processes attacker-supplied data under the victim shop's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
