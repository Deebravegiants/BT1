### Title
Webhook HMAC Does Not Bind `shop`/`topic`/`webhook-id` Metadata to Signature, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` only signs the raw request body with HMAC, while the `shop`, `topic`, `webhook-id`, and `api-version` values used by application handlers are read directly from unauthenticated HTTP headers. Any actor who legitimately receives one genuine webhook (e.g., by installing the app on their own store) can capture a valid `(body, hmac)` pair and replay it with a different `x-shopify-shop-domain` header value, causing the app to process the payload as if it originated from a victim's shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate_signature` computes the HMAC over exactly that signable string and compares it to the value from the `hmac-sha256` header: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read straight from headers with no cryptographic tie to the signature: [3](#0-2) 

`Registry.process` validates only the HMAC and then forwards the unauthenticated `request.shop` value straight into the handler payload: [4](#0-3) 

The identity binding that should hold is: `shop asserted in header == shop covered by HMAC`. Because the signature covers only the body, this equality is never checked — the same `(body, hmac)` pair remains valid under the shared, app-wide `api_secret_key` regardless of which `x-shopify-shop-domain` value accompanies it. This is the same root-cause class as the referenced Fabric CVE-2022-31121: a request-processing boundary trusts unvalidated attacker-influenced fields that determine downstream trust decisions.

### Impact Explanation
Because `api_secret_key` is shared by the app across all of its installed shops (it is not per-shop), a webhook payload/HMAC pair captured from one (attacker-controlled, unprivileged) shop installation remains cryptographically valid when replayed with an arbitrary `shop-domain` header. The app's webhook handler receives `WebhookMetadata` with a forged `shop` value and legitimate-looking, HMAC-"verified" status, enabling cross-tenant data injection/spoofing (e.g., causing the host app to write attacker-controlled order/customer data under a victim shop's tenant record). This matches the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Exploitation only requires the attacker to be an ordinary, unprivileged internet user who installs the app on their own Shopify store (a normal onboarding flow) to receive one legitimate webhook delivery, then replay that captured request to the app's webhook endpoint with a modified `shop-domain`/`topic` header. No `api_secret_key`, access token, or privileged account for the victim shop is needed, and no TLS interception is required since the attacker owns the original webhook delivery.

### Recommendation
Bind the shop (and ideally topic/webhook id) to the HMAC verification by including them in the signable content, or by cross-checking `request.shop` against the shop that was independently established via a trusted mechanism (e.g., session/tenant lookup) rather than trusting the raw header value once HMAC-of-body-only passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a legitimate webhook (e.g., `orders/create`), capturing the raw body `B` and the `x-shopify-hmac-sha256` header value `H` Shopify computed with the app's `api_secret_key`.
2. Attacker sends a POST to the app's webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Webhooks::Request.new` accepts the request (all required headers present), and `HmacValidator.validate` succeeds because it only recomputes the HMAC over `B`, matching `H`: [5](#0-4) 
4. `Registry.process` proceeds to invoke the handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, even though that shop never sent this webhook: [6](#0-5)

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
