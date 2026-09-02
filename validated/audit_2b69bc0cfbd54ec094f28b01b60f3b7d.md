### Title
Webhook shop/topic spoofing via header fields not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , so `Utils::HmacValidator.validate(request)` only proves that the *body* bytes were signed by Shopify with the app's secret [2](#0-1) . The `shop`, `topic`, and `webhook_id` values that `Registry.process` trusts and hands to the app's handler are read straight from HTTP headers and are never part of the signed material [3](#0-2) .

### Finding Description
`Registry.process` validates the HMAC and then immediately dispatches on `request.topic` and forwards `request.shop` to the handler as the tenant identifier, with no additional binding between the verified body and these header-derived fields: [4](#0-3) 

The equality this breaks is: `shop authenticated (bytes covered by HMAC) == shop acted on by handler (WebhookMetadata#shop, from header)`. Because the app's `client_secret` is shared across all shops that install the app, any merchant who installs the app on their own shop legitimately receives real, validly-signed `(raw_body, hmac)` pairs from Shopify. Since the signature never binds `shop-domain`, `topic`, or `webhook-id` headers, that same merchant can resend the identical HTTP body/HMAC pair to the app's single webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) headers to impersonate a different shop. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` will invoke the handler with `WebhookMetadata.new(topic: ..., shop: <attacker-chosen-shop>, ...)` [5](#0-4) .

### Impact Explanation
This lets a merchant who is unprivileged with respect to another tenant forge webhook events attributed to that other tenant's `shop` value, causing the app to process/store attacker-controlled data under a victim shop's identity — a cross-tenant data-integrity/confusion issue in code the gem controls (`Request` and `Registry`), not something the host application can avoid without adding its own extra verification on top of what this gem exposes.

### Likelihood Explanation
Any merchant who installs the app (a low-privilege, unauthenticated-relative-to-other-tenants actor) can capture their own legitimate webhook traffic (their app endpoint is reachable and receives real `(body, hmac)` pairs directly from Shopify) and replay it with modified `shop-domain`/`topic`/`webhook-id` headers against the same public endpoint. No secrets, tokens, or TLS interception are required — only observation of one's own inbound webhook traffic, which is inherently visible to the receiving app owner.

### Recommendation
Bind the header-derived identity fields (`shop`, `topic`, `webhook_id`) into the value that is verified, or otherwise cryptographically tie them to the signed body (e.g., include them in `to_signable_string`, or have `Registry.process` cross-check `request.shop` against the shop the registration/session belongs to before invoking the handler). At minimum, document and enforce that consumers must independently verify `request.shop` against a known/expected tenant before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and lets it receive one legitimate webhook (e.g. `orders/create`), capturing the raw POST body and the `x-shopify-hmac-sha256`, `x-shopify-topic`, `x-shopify-shop-domain`, `x-shopify-webhook-id` headers exactly as sent by Shopify.
2. Attacker resends the exact same HTTP request to the app's webhook endpoint, keeping the body and `x-shopify-hmac-sha256` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`/`x-shopify-webhook-id` if the app maps by topic).
3. `Webhooks::Request.new` parses headers/body normally [6](#0-5) ; `Utils::HmacValidator.validate(request)` succeeds because it only hashes `@raw_body`, unchanged from step 1 [1](#0-0) .
4. `Registry.process` finds the handler for the (possibly attacker-chosen) topic and invokes it with `shop: "victim-shop.myshopify.com"` even though that shop never sent this webhook [4](#0-3) , causing the app's downstream logic to act on/attribute data to the victim tenant.

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
