## Title
Webhook Shop Identity Not Bound to HMAC Signature Allows Cross-Tenant Webhook Spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shop-domain` header — which is *not* covered by that signature — as the tenant identity passed to the app's handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes the signature exclusively over `verifiable_query.to_signable_string`: [2](#0-1) 

`Registry.process` validates the HMAC and then, on success, immediately trusts `request.shop` (sourced from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header) as the tenant identity forwarded to the app's handler: [3](#0-2) 

`request.shop` reads directly from headers with no cross-check against the signed body: [4](#0-3) 

The identity binding that should hold is: `shop_used_for_tenant_lookup == shop_covered_by_hmac`. Here, the shop value acted upon (used to attribute the webhook payload to a merchant in `WebhookMetadata`) is a field that is not covered by the HMAC — exactly the class of flaw highlighted in the reference report, where a value used for matching/attribution is not bound to the value that was actually verified.

### Impact Explanation
An attacker who legitimately installs the app on their own store (a fully unprivileged, self-service action requiring no special credentials) can capture one of their own store's genuine, Shopify-signed webhook deliveries (valid `raw_body` + valid HMAC for that body, since Shopify computes the HMAC over the body only). They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value (e.g., a victim shop's domain). Because the HMAC check in `HmacValidator.validate_signature` never inspects the shop header, the forged request passes validation, and `Registry.process` hands the handler a `WebhookMetadata` object whose `shop` field claims to be the victim tenant while the body content actually originated from the attacker's own store. Any host application that uses `data.shop` from `WebhookMetadata` to select the merchant/session context for processing the webhook body (which is the intended and documented use of this field) will attribute attacker-controlled data to another tenant — a cross-tenant integrity/confusion issue reachable by any unprivileged internet user who can install the app once.

### Likelihood Explanation
Likelihood is high: the only prerequisite is the ability to install the app on a store the attacker controls (self-service, no privileged credentials needed), after which capturing and replaying an HTTP request with a modified header requires no cryptographic secret.

### Recommendation
Include the shop domain (and other identity-relevant headers such as topic and API version) in the signed material, or alternatively cross-validate the `shop-domain` header against `session`/registration state before trusting it, so that the value used for tenant attribution is provably bound to the value verified by the HMAC.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com`.
2. Attacker triggers a webhook event (e.g., `orders/create`) on their own store, capturing the raw POST body and the `x-shopify-hmac-sha256` header Shopify sends.
3. Attacker replays the identical body + HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `@raw_body`, per `Webhooks::Request#to_signable_string`.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` invokes the app handler with `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker's data>, ...)`, causing attacker-supplied data to be processed under the victim tenant's identity.

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
