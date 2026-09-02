### Title
Webhook `shop` attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (tenant) value from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, while `Utils::HmacValidator` only verifies the HMAC over the raw request body. The `shop` field that the rest of the pipeline treats as the authenticated tenant identity is never bound to the signature, so any actor who can produce one validly-signed webhook body (e.g. by owning a shop that installs the app) can relabel that body as belonging to a different shop and have it processed as if it originated from that other tenant.

### Finding Description
`Webhooks::Registry.process` accepts a `Request`, checks only `Utils::HmacValidator.validate(request)`, and then dispatches to the app's handler using `request.shop` for tenant attribution: [1](#0-0) 

`HmacValidator.validate` computes the signature exclusively from `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only the raw body, while `shop` is read straight from a header that is not part of the signed material at all: [3](#0-2) 

Because the app's `client_secret`/`api_secret_key` used to compute the HMAC is a single, fixed value shared across every merchant shop that installs the app (it is not shop-specific), a valid `(body, hmac)` pair proves only "this body was signed by someone who possesses the app's secret" — it proves nothing about *which* shop the body belongs to. The `shop` value that identifies the tenant is carried in a header that sits entirely outside the HMAC's coverage.

This breaks the intended identity binding:
`shop authenticated by HMAC == shop used as the tenant/session key by the handler`

In reality: `shop authenticated by HMAC` is undefined (the signature says nothing about shop), while `shop used as the tenant/session key` is attacker-controllable via the header.

### Impact Explanation
An app that installs on multiple merchant shops uses one webhook endpoint and one `client_secret` for all of them. A merchant who installs the app (an "unprivileged" party relative to other tenants of the same app) can capture a legitimately-signed webhook `(raw_body, x-shopify-hmac-sha256)` pair delivered to that shared endpoint for their own shop, then replay the identical body/HMAC while substituting the `shopify-shop-domain` header for a victim shop. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` forwards `shop: request.shop` (the attacker-chosen value) to the app's handler as `WebhookMetadata#shop`. Any app logic that looks up the victim's session/access token or writes data keyed by this `shop` value will act on the victim tenant using attacker-supplied body content — a cross-tenant data/session confusion that satisfies the Critical "cross-tenant access" bar.

### Likelihood Explanation
Exploitation requires only the ability to install the app on any single shop (a normal, unprivileged action available to any merchant/developer) and the ability to send a crafted HTTP request to the app's public webhook endpoint with a substituted `shopify-shop-domain` header — no access token, `api_secret_key`, or victim credentials are required. The one non-trivial requirement is capturing one valid `(body, hmac)` pair, which is straightforward since the attacker fully controls a shop that can trigger webhook events (e.g. `orders/create`) to their own installation.

### Recommendation
Bind the `shop` (and other host-application-consumed identifiers such as `topic`/`webhook_id`, if used for authorization decisions) into the HMAC-verified material, or otherwise cryptographically tie the header-derived `shop` to the specific installation's stored HMAC secret/session rather than trusting the header value as-is. At minimum, `Webhooks::Request#to_signable_string` should not exclude the tenant-identifying header from what is verified, and `Registry.process`/consuming apps should cross-check `request.shop` against an independently-verified source (e.g., the session associated with the specific shop that installed the app) before trusting it for tenant attribution.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the exact `raw_body` and the `x-shopify-hmac-sha256` value sent by Shopify to the app's shared webhook endpoint.
2. Attacker replays the identical HTTP request to the same endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this successfully [4](#0-3) , `HmacValidator.validate` passes because it only checks `raw_body` against the (unchanged) HMAC [5](#0-4) , and `Registry.process` invokes the app's handler with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body` [6](#0-5) .
4. Any handler logic keyed on `data.shop` (e.g. loading the victim's session/access token or writing to victim-scoped storage) now operates on attacker-supplied data under the victim's tenant identity.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
