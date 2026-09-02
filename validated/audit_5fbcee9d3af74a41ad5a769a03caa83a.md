Confirmed: the webhook HMAC signs only the raw body, and `shop` (from the `X-Shopify-Shop-Domain`/`shopify-shop-domain` header) is passed unauthenticated into the handler's `WebhookMetadata`, matching the report's identity-binding bug class.This confirms the design: the docs explicitly claim `Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0) , and `data.shop` is presented to handlers as the trusted "shop domain of the webhook" [2](#0-1) , yet `shop` is populated straight from an unauthenticated header rather than the HMAC-verified payload.

### Title
Webhook `shop` identity field is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook solely by checking `Utils::HmacValidator.validate(request)`, and that validator signs/verifies only `request.to_signable_string`, which for `Webhooks::Request` is the raw HTTP body [3](#0-2) . The `shop` value that gets handed to the app's handler as the trusted tenant identifier is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [4](#0-3) , a value that is never included in the HMAC computation. This breaks the identity binding: `HMAC-authenticated bytes (raw_body only) ≠ shop identity acted upon (header value)`.

### Finding Description
`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it via `OpenSSL.secure_compare` [5](#0-4) . For webhooks, `to_signable_string` returns only `@raw_body` [3](#0-2) ; the `shop`, `topic`, `api_version`, and `webhook_id` accessors are all pulled unauthenticated from headers [6](#0-5) .

`Registry.process` uses this same unauthenticated `request.shop` as the tenant identity handed to the app's handler: it validates only the HMAC, then builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` [7](#0-6) . The gem's own documentation tells developers that `process` "will verify the request did indeed come from Shopify" [1](#0-0)  and that `data.shop` is "The shop domain of the webhook" [2](#0-1)  — i.e. the library's documented contract is that a validated request implies a validated shop, which is false.

Because a single app-level `client_secret` (`Context.api_secret_key`) signs webhooks for every shop that installs the app [8](#0-7) , any unprivileged merchant who has installed the app on their own store legitimately receives a genuine `(raw_body, hmac)` pair for their own shop. That merchant can replay that exact body+HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never looks at the shop header), and `Registry.process` forwards the attacker-chosen `shop` value straight to the host app's handler as if it were verified, since nothing in the gem cross-checks `request.shop` against the shop that the HMAC-secret actually belongs to on a per-request basis.

### Impact Explanation
This is a cross-tenant identity confusion inside the gem's own webhook-processing API: the tenant/shop discriminator that host apps are told to trust from a "verified" webhook is fully attacker-controlled while the payload signature check passes. A host application built strictly against this gem's documented contract (validated request ⇒ trustworthy `data.shop`) will attribute attacker-controlled webhook bodies (with a genuine signature for the attacker's own shop) to a victim shop, causing cross-tenant data confusion/injection keyed by `data.shop`.

### Likelihood Explanation
Any unprivileged internet user who can install the app on their own store (a normal, non-privileged install flow) automatically obtains a valid `(raw_body, hmac)` pair for their own shop's webhooks, with no need for `api_secret_key`, tokens, or any privileged access. Crafting the replayed HTTP request with a different `shop`-domain header requires no special capability beyond a standard HTTP client.

### Recommendation
Include the shop domain (and other identity-relevant fields such as topic and webhook_id) inside the signable string used for HMAC verification, or otherwise cryptographically bind `request.shop` to the signed payload before it is trusted by `Registry.process`/`WebhookMetadata`. At minimum, update `HmacValidator`/`Webhooks::Request` so `to_signable_string` covers the header-derived `shop` value, and document that `data.shop` should be cross-checked by the host app against its own known-shop list rather than treated as verified purely because the HMAC matched.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, receiving a genuine webhook: raw body `B`, header `shopify-shop-domain: attacker.myshopify.com`, header `shopify-hmac-sha256: H` (computed as `HMAC-SHA256(client_secret, B)`).
2. Attacker crafts a new HTTP POST to the app's webhook endpoint with the same body `B` and the same `shopify-hmac-sha256: H`, but sets `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers/body [9](#0-8) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, B)` and matches `H`, so validation succeeds [10](#0-9) .
5. `Registry.process` dispatches `WebhookMetadata.new(shop: "victim.myshopify.com", body: JSON.parse(B), ...)` to the app's handler, which — per the gem's own documented contract — treats this as a verified webhook for `victim.myshopify.com` [11](#0-10) .

### Citations

**File:** docs/usage/webhooks.md (L12-18)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```

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
