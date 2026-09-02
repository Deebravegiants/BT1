### Title
Webhook shop identity used for tenant dispatch is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#hmac` is verified against the HMAC-signable string derived **only** from the raw JSON body, while the `shop` (tenant identity) used to dispatch the payload to the app's webhook handler is read from an HTTP header that is never included in that signable string. This breaks the binding `hmac_covers(shop) == shop_used_for_dispatch`.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 

`Request#shop` is populated straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the signature purely against `verifiable_query.to_signable_string` (i.e. the body) and the app's `api_secret_key`: [3](#0-2) 

`Registry.process` validates the HMAC and then unconditionally trusts `request.shop` for constructing `WebhookMetadata`, which is the tenant identity handed to the app's handler: [4](#0-3) 

Because the shop header is not part of the signed bytes, the equality that should hold — "the shop the HMAC authenticates" == "the shop the handler acts on" — does not hold. Any actor who possesses one valid `(body, hmac)` pair signed by the app's secret (e.g., a legitimate webhook delivery to their own store — a normal, unprivileged merchant using the same app) can replay that exact body/HMAC pair while substituting the `x-shopify-shop-domain` header to name a different, victim shop. `HmacValidator.validate` still succeeds because it never looks at the header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop.

### Impact Explanation
This allows cross-tenant event injection: the app's webhook handler (and any app logic keyed off `WebhookMetadata#shop`, e.g. persisting data, updating per-shop state, triggering shop-specific side effects) will act as if the victim shop generated the event, even though the payload actually originated from — and was HMAC-signed for — a different shop. This is a cross-tenant access vector satisfying the "Critical — cross-tenant access" impact bar, since the identity boundary between tenants (shops) that the app relies on this gem to enforce is not actually enforced by the gem's own signature check.

### Likelihood Explanation
Exploitability requires only that the attacker be a shop owner/user of the same third-party app (an unprivileged relationship with respect to other tenants of that app) who receives at least one real webhook delivery for their own shop. No access to `api_secret_key`, access tokens, or the target shop's credentials is required — only replay of a header value that is entirely attacker-controlled and unauthenticated in this gem's verification path.

### Recommendation
Bind the shop identity to the signed material before it is trusted for dispatch:
- Reject/flag the header-derived `shop` unless it is corroborated by another authenticated channel (e.g., cross-check against the shop associated with the resolved `webhook_id`/subscription via an authenticated lookup), or
- At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used by consuming apps as a tenant boundary without additional verification, and provide/require a mechanism (e.g., comparing against a known list of registered shops for the given `webhook_id`) before dispatch.

### Proof of Concept
1. App merchant "Attacker" has the app installed on `attacker-shop.myshopify.com` and receives a legitimate webhook delivery (e.g. `orders/create`) from Shopify with headers:
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC of raw_body under the app's api_secret_key>`
2. Attacker POSTs the identical `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint again, but changes the header to:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Request.new` parses this successfully (only checks header *presence*, not shop binding): [5](#0-4) 
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because it only recomputes/compares the HMAC over `@raw_body`, which is unchanged.
5. `ShopifyAPI::Webhooks::Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, even though the actual signed data belongs to `attacker-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
