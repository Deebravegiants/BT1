### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop`, `topic`, `webhook_id`, and `api_version` values used to dispatch and attribute the webhook are taken from unauthenticated HTTP headers. An attacker who legitimately receives a validly-signed webhook for their own store (which they fully control) can replay the same body/HMAC pair to a victim app's webhook endpoint while substituting a different `shop-domain` header, causing the gem to report a different, attacker-chosen shop identity to the handler even though only the body was actually verified.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the received HMAC: [1](#0-0) 

For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only the raw request body — none of the Shopify-supplied headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) are part of the signed material: [2](#0-1) 

`Registry.process` uses that same unauthenticated `shop` (and `topic`, `webhook_id`, `api_version`) header value to look up the handler and to construct the `WebhookMetadata` passed to the app's business logic, after only checking the body HMAC: [3](#0-2) 

The identity binding the gem implicitly claims to enforce is:
`shop reported to handler == shop that Shopify actually signed the webhook for`

But the actual binding enforced is only:
`HMAC(raw_body, api_secret_key) == received_hmac`

Since `shop-domain` is not part of `raw_body` or the signed string, these two are not equivalent. Any request whose body+HMAC pair is valid (for *any* shop that installed the app and can trigger a webhook to itself) can be replayed with an arbitrary `shop-domain` header value, and the signature check will still pass — while `request.shop` used by the handler will reflect the attacker-controlled value, not the shop Shopify actually generated the webhook for.

### Impact Explanation
This breaks the shop/tenant identity boundary the gem is expected to guarantee to consuming applications: `Registry.process` hands the handler a `WebhookMetadata` with `shop: request.shop`, which application code typically uses as the tenant key to look up sessions, write data, or trigger business logic per merchant. An attacker who is a legitimate merchant using the app can trivially forge a webhook delivery apparently coming from a *different* victim shop while it carries a validly-computed HMAC, resulting in cross-tenant data confusion/injection at the application layer that consumes this gem's webhook verification as its sole trust mechanism.

### Likelihood Explanation
Likelihood is high for any app using this gem's webhook processing as documented: the attacker only needs to be a legitimate, unprivileged merchant (able to install the app and receive one webhook to themselves), and is never required to know `api_secret_key`. No interception of Shopify's traffic is needed — the attacker can capture a body+HMAC pair addressed to themselves and directly send a forged request to the app's public webhook endpoint with a different `shop-domain` header.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the material the HMAC is computed over, or otherwise cryptographically bind the identifying headers to the signed body before trusting them in `Registry.process`/`WebhookMetadata`. At minimum, `Request#to_signable_string` should include the `shop`, `topic`, and `webhook_id` headers so that tampering with any of them invalidates the HMAC.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers it for any webhook topic (e.g. `customers/update`).
2. Shopify delivers a legitimately signed webhook to the app's registered endpoint (or to any endpoint the attacker controls, since they own that shop) with headers:
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC of raw body>`
   - raw body `B`
3. Attacker captures `B` and the valid HMAC.
4. Attacker sends a new POST request directly to the app's webhook endpoint with the same body `B` and same HMAC header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `HmacValidator.validate` succeeds (body/HMAC unchanged), `Registry.process` dispatches the handler with `WebhookMetadata.shop == "victim.myshopify.com"`, even though Shopify never generated this webhook for that shop. [4](#0-3) [3](#0-2)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
