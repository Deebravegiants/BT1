### Title
Webhook `shop` (tenant) attribution is not covered by the HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (and `topic`, `webhook_id`) values used to route and attribute the webhook to a tenant are taken from unauthenticated HTTP headers. Any shop that legitimately installs the app can capture one of its own validly-signed webhook deliveries and replay the same body/HMAC pair to the app's webhook endpoint while substituting a victim shop's domain in the `x-shopify-shop-domain` header. `HmacValidator` still reports the signature as valid because it never inspected the header, so the handler processes attacker-supplied data as if it originated from the victim tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are read straight from HTTP headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `to_signable_string`, i.e., the body — it never verifies that the `shop` header is consistent with anything: [3](#0-2) 

`Registry.process` trusts this unauthenticated header to build the tenant-identifying `WebhookMetadata` passed to the app's handler: [4](#0-3) [5](#0-4) 

The identity binding that should hold is:
`shop authenticated by the HMAC signature == shop used as the tenant/session key by the handler`

In reality, the HMAC only authenticates the *body bytes* using the app's shared `api_secret_key` — it says nothing about which shop the payload was generated for. Because the same `api_secret_key` is used across every shop that installs the app, an attacker who controls their own (legitimately installed) shop receives real, validly-signed webhook deliveries for their own shop. They can replay that exact body + `x-shopify-hmac-sha256` value against the app's webhook endpoint, only changing `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id` if desired) to point at a different, victim shop. `HmacValidator.validate` still returns `true` since it never looks at those headers, and `Registry.process` dispatches the forged `WebhookMetadata` with `shop: <victim-shop>` and attacker-chosen `body` straight to the app's handler.

### Impact Explanation
This breaks the tenant isolation boundary the library is expected to provide to host applications: it allows one tenant (shop) to inject attacker-controlled event data that the application's webhook handler will attribute to another tenant. Depending on how the host app's handler uses `WebhookMetadata#shop` and `#body` (e.g., updating that shop's local records, triggering emails, syncing inventory/orders, GDPR data requests), this is a cross-tenant data injection / cross-tenant access vector purely through this gem's own verification logic, matching the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Any user can sign up for a Shopify development store and install an app that uses this library (this is the normal, unprivileged onboarding flow for third-party integrations), which is enough to obtain a legitimately HMAC-signed webhook body/signature pair for their own shop. Replaying that body with a substituted `shop` header requires only basic HTTP tooling — no access token, secret, or privileged account is needed, satisfying the "unprivileged internet user" threat model.

### Recommendation
Bind the tenant identity into the verified material instead of trusting an unauthenticated header:
- Require applications (or add built-in support) to cross-check the `shop` header against a shop known to have installed the app / have an active session for the given `webhook_id`/topic before dispatching to the handler, rather than trusting the header value alone.
- At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC and that handlers must independently verify the shop is one with a valid, stored session/install record before acting on the payload.
- Consider incorporating the `shop`, `topic`, and `webhook_id` headers into the value that is HMAC-verified (where Shopify's delivery mechanism allows it) so that any tampering with those headers invalidates the signature.

### Proof of Concept
1. Attacker installs the target app on their own development store `attacker-shop.myshopify.com`, causing Shopify to deliver a legitimate webhook (e.g. `orders/create`) with a valid `x-shopify-hmac-sha256` computed over the raw body using the app's `api_secret_key`.
2. Attacker captures `raw_body` and the `x-shopify-hmac-sha256` value from that delivery.
3. Attacker sends a new POST request to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and any desired `x-shopify-topic` under an app-registered topic).
4. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only and confirms a match, since the signature never depended on the `shop` header: [6](#0-5) 
5. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)` and invokes the registered handler, which now processes attacker-controlled data as if it were an authentic event from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
