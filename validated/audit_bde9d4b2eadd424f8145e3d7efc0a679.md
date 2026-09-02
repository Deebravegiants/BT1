### Title
Webhook shop-domain identity is trusted but not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while `ShopifyAPI::Webhooks::Registry.process` trusts the unauthenticated `shop-domain` (and `topic`/`webhook-id`) headers as the tenant identity forwarded to the app's webhook handler. This mirrors the ERC4626 report's root cause: a value that participates in a downstream trust decision (`totalVaultCollateral()` / here, the shop identity) is not bound by the same integrity check that protects the rest of the state (share-price math / here, the HMAC signature).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are read straight from HTTP headers, never mixed into `to_signable_string`: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the signature over `verifiable_query.to_signable_string`, i.e. the body bytes, and never over the shop/topic/id headers: [3](#0-2) 

Yet `Registry.process` uses `request.shop` — the unauthenticated header — as the tenant identity that is handed to the consuming application's handler alongside the (verified) body: [4](#0-3) 

So the binding the library implicitly claims to provide is:
`hmac_valid(raw_body) == true` implies `(shop, topic, body)` is authentic.

But the actual guarantee is only:
`hmac_valid(raw_body) == true` implies `body` bytes are unmodified — `shop` is asserted, not verified.

Equality that should hold: `shop_header == shop_bound_by_hmac`. In this code it does not — `shop_bound_by_hmac` is undefined because the header is entirely outside the signed payload.

### Impact Explanation
Any party who can present the app with a `(raw_body, valid_hmac)` pair for one tenant (e.g., their own installed shop) can freely relabel the `x-shopify-shop-domain` header to attribute that payload to a different tenant, and `HmacValidator.validate` will still return `true`, because the check never inspects the header. Since `Registry.process` immediately forwards `request.shop` to the host application's handler as the trusted tenant identifier without any additional consistency check within this gem, this is a cross-tenant identity-binding break: data or events legitimately signed for shop A can be delivered to, and processed as belonging to, shop B. Any app logic that keys persistence, authorization, or session lookups off `WebhookMetadata#shop` inherits this confusion directly from the gem's `process` API.

### Likelihood Explanation
This requires no secret material: any actor able to reach the app's public webhook endpoint (which by design accepts unauthenticated internet traffic, gated only by the HMAC) and who possesses one genuine `(body, hmac)` pair — trivially obtainable by installing the app on any store, even the attacker's own free/dev store, and observing a delivered webhook — can replay it with a forged shop header. No `api_secret_key`, access token, or privileged account is required, satisfying the unprivileged-internet-user constraint.

### Recommendation
Include the tenant-identifying headers (`shop-domain` at minimum, ideally `topic` and `webhook-id`) in the signed/verified material, or otherwise cryptographically bind them to the body before `Registry.process` treats `request.shop` as trustworthy — e.g., require the caller to supply the shop from a source already bound to the OAuth-established session, and assert it matches the header, rather than trusting the header outright.

### Proof of Concept
1. Install the app on shop `attacker.myshopify.com`; trigger any webhook (e.g., `orders/create`) to obtain a genuine `(raw_body, X-Shopify-Hmac-Sha256)` pair signed with the real `client_secret` — the attacker never sees the secret itself.
2. Replay the same body and HMAC header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged header without error (see header handling at [5](#0-4) 
).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because only `raw_body` is checked ( [6](#0-5) 
).
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the payload was never issued for that shop, demonstrating the broken identity binding.

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
