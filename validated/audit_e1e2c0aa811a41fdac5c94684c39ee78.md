### Title
Webhook Shop-Domain Header Is Not Covered by HMAC, Allowing Cross-Tenant Shop Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates its HMAC over the raw request body only. The `shop-domain` header — which `ShopifyAPI::Webhooks::Registry.process` passes on to the app's handler as the authoritative tenant identifier — is never included in the signed material. Anyone who can obtain one legitimately-signed webhook body/HMAC pair (trivial for an attacker who installs the app on their own store) can replay that exact body with a different `x-shopify-shop-domain` header and have it pass HMAC validation while being attributed to an arbitrary victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the unauthenticated header, with no cryptographic link to the body that was signed: [2](#0-1) 

`HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` against `verifiable_query.hmac`, i.e. it only proves that the *body* was signed by a holder of the app's secret — it says nothing about which shop sent it: [3](#0-2) 

`Registry.process` treats a passing HMAC check as sufficient authorization to dispatch the handler, then hands the handler `request.shop` (the unauthenticated header value) as the tenant identity for the event: [4](#0-3) 

The binding being broken is: *shop claimed in the "shop-domain" header* == *shop the HMAC actually authenticates*. Because the shop header is excluded from the signed bytes, this equality never holds — the gem verifies bytes (the body) that are disjoint from the bytes it later trusts as tenant identity (the header).

### Impact Explanation
Any external actor who can install the target app on a shop they control (a normal, unprivileged flow — merchant self-serve installs are the intended way apps get access) receives real, validly-signed webhook deliveries for their own shop. Because the signature covers only the body, the attacker can replay that same body+HMAC pair directly to the app's public webhook endpoint while substituting `x-shopify-shop-domain` (or `shopify-shop-domain`) with a victim shop's domain. `Registry.process` will accept the request (HMAC check passes, since it's checking body/secret only) and invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop, even though nothing about the victim shop was actually verified. Any app logic that keys off `data.shop` (session lookup, tenant-scoped data writes, order/customer processing, etc.) executes under a forged tenant identity — a cross-tenant confusion primitive that is squarely the "cross-tenant access" class of impact.

### Likelihood Explanation
Requires only: (1) the ability to install the target app on any shop (self-service, no special privilege), to harvest one valid `(body, hmac)` pair, and (2) the ability to send an HTTP POST directly to the app's public webhook endpoint with an attacker-chosen `shop-domain` header — both are within reach of any unprivileged internet user, with no access token, `api_secret_key`, or credential theft required.

### Recommendation
Bind the shop/topic/webhook identity into the material that is verified, not just the raw body. At minimum, `Request#to_signable_string` (or a parallel check in `Registry.process`) should incorporate the `shop-domain` (and ideally `topic`/`webhook-id`) header into the value verified against the HMAC, or `Registry.process` should independently confirm that the shop asserted in the header corresponds to a shop already known to have installed the app (e.g., cross-reference an existing session) before dispatching the handler with that shop value.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com`; capture a real webhook delivery, e.g. `orders/create`, noting `raw_body` and the `x-shopify-hmac-sha256` header — this HMAC validates fine via `HmacValidator.validate` because it only checks `raw_body` against the app's secret: [5](#0-4) 
2. Send a POST to the app's webhook endpoint reusing the identical `raw_body` and `x-shopify-hmac-sha256`, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Request.new` accepts the headers (all required headers are present): [6](#0-5) 
4. `Registry.process` validates the HMAC successfully (it never inspects `shop`) and calls `handler.handle` with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` now returns `"victim-shop.myshopify.com"`: [7](#0-6) 
5. Any handler logic keyed on `data.shop` now operates believing the event genuinely originated from the victim shop.

### Citations

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
