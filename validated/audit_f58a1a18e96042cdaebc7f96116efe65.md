## Analysis

I found a concrete case of the described bug class: **a field is acted upon (and passed to application logic) without being covered by the HMAC signature** — in `lib/shopify_api/webhooks/request.rb`.

### The binding that should hold
`request.shop` (and `request.topic`) used by the handler ⟺ bytes actually covered by `HmacValidator.validate`

### Root cause

`ShopifyAPI::Webhooks::Request#to_signable_string` returns **only the raw body**: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are read straight from HTTP headers with no cryptographic binding to the signature at all: [2](#0-1) 

`HmacValidator.validate` only ever checks `to_signable_string` (i.e., the raw body) against the secret: [3](#0-2) 

`Registry.process` treats a passing HMAC check as proof that the *entire request*, including `request.shop`, is authentic, and forwards the unauthenticated `shop` value straight into the handler's `WebhookMetadata`: [4](#0-3) 

Because the `api_secret_key` is a single **app-wide** secret shared across every installed shop (not a per-shop secret), any merchant who has legitimately installed the app receives real, validly-signed webhook deliveries for their own shop. Since the `shop-domain` header isn't part of the signed bytes, that same merchant can replay the identical `(body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` will still succeed (the body/secret pair is unchanged), so `Registry.process` will dispatch the handler with `WebhookMetadata#shop` set to the attacker-chosen tenant.

### Impact
If the host application relies on `WebhookMetadata#shop` to determine which tenant's data/records/credentials the webhook body applies to (which is the intended and documented use, per `docs/usage/webhooks.md`), this allows a merchant who is a customer of the app to inject data attributed to a different, unrelated shop into the app's multi-tenant processing pipeline — a cross-tenant integrity break using only their own legitimate webhook traffic, no `api_secret_key` needed.

### Title
Webhook `shop`/`topic` fields are unauthenticated (not covered by HMAC), enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the HMAC signature to the raw body only, while `shop`, `topic`, and `webhook_id` are taken unauthenticated from HTTP headers and passed to the application's webhook handler as if fully verified.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `to_signable_string`, which for `Webhooks::Request` returns `@raw_body` alone [5](#0-4) . The `shop`, `topic`, and `webhook_id` accessors read directly from the (attacker-controllable, since this is an inbound HTTP endpoint) header hash [6](#0-5) . `Registry.process` gates dispatch solely on `Utils::HmacValidator.validate(request)` succeeding, then forwards `request.shop`/`request.topic` into `WebhookMetadata` without any further binding check [4](#0-3) . Because `api_secret_key` is one value shared for the whole app across all installed shops [7](#0-6) , any merchant that has installed the app can obtain a valid `(raw_body, hmac)` pair from a real Shopify-delivered webhook for their own shop, then resubmit that exact pair to the app's webhook controller while changing only the `shopify-shop-domain` (and/or `shopify-topic`) header. Validation passes because the signed bytes are unchanged, and the handler receives an unauthenticated, attacker-chosen `shop` value it believes is verified.

### Impact Explanation
This breaks the identity binding "verified sender's shop == shop value the handler acts on." The impact is cross-tenant contamination of webhook-driven processing: the attacker's genuine (but replayed/re-labeled) payload can be attributed to any other tenant shop known to the app, since `shop` is the field host applications use to scope per-tenant data/actions from webhook processing (as documented in `docs/usage/webhooks.md`).

### Likelihood Explanation
Any existing customer of the app (an "unprivileged internet user" relative to other tenants) can perform this without needing `api_secret_key`, an access token, or any privileged access — only their own normal webhook traffic, which Shopify delivers to them by design. The endpoint is a public HTTP route by definition (per `docs/usage/webhooks.md`'s `WebhookController`).

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed/verified material, or otherwise cryptographically bind them (e.g., include them in `to_signable_string`, or independently verify `shop` against the session/tenant that legitimately owns the delivery channel) before trusting them for tenant attribution in `WebhookMetadata`.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com`; attacker controls that shop and captures a real webhook delivery: `raw_body = B`, header `shopify-hmac-sha256 = H`, header `shopify-shop-domain = shop-a.myshopify.com`.
2. Attacker POSTs the same `B` and `H` to the app's webhook endpoint, but sets `shopify-shop-domain: shop-b.myshopify.com`.
3. `Webhooks::Request.new` accepts it (all required headers present) [8](#0-7) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` [3](#0-2) , so validation passes.
5. The handler is invoked with `WebhookMetadata(shop: "shop-b.myshopify.com", body: B, ...)` [9](#0-8) , even though `shop-b` never sent this webhook and `B` was never generated for it.

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
