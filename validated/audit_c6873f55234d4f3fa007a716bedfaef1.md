### Title
Webhook shop-domain header is not covered by the HMAC, allowing cross-tenant replay of a legitimate webhook - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the caller-supplied `shop-domain` header straight to the handler as the tenant identifier, without that header ever being covered by the signature.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the signature against `verifiable_query.to_signable_string`, and for a webhook `Request`, `to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

Meanwhile, `shop`, `topic`, and `webhook_id` are read directly from attacker-controllable HTTP headers with no cryptographic binding to the signed body: [3](#0-2) 

`Registry.process` validates only the HMAC, then dispatches to the handler using the unverified `shop` header as the tenant key: [4](#0-3) 

The equality that the design implicitly assumes is: `shop header == shop that produced/authorized this HMAC-signed body`. In fact the code only proves `HMAC(raw_body, api_secret_key) == received_hmac`; it proves nothing about which shop the header claims. Because `shop-domain` (and `topic`/`webhook-id`) sit outside the signed content, any request with a *valid* HMAC/body pair can be replayed with an arbitrary `shop-domain` header and will still pass verification.

### Impact Explanation
An attacker who legitimately installs the app on their own (low-privilege, unprivileged) shop will receive real, validly-signed webhook deliveries for that shop. Because `shop` is not part of the signed payload, the attacker can replay that same body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain. `Registry.process` will accept it (HMAC checks out) and invoke the handler with `WebhookMetadata#shop` set to the victim's domain, causing the host application — which typically keys per-tenant state/lookups off this `shop` field — to process attacker-controlled webhook data under the identity of a different tenant. This is a cross-tenant identity-binding break (the "acted-upon" field, `shop`, is not covered by the verified bytes), matching the Critical "cross-tenant access" category.

### Likelihood Explanation
The prerequisite is only that the attacker be an ordinary, unprivileged merchant/user of the target app (able to install it on a shop they control and observe the webhooks it receives) — no access to `api_secret_key`, tokens, or any privileged credential is required. Capturing one's own legitimate webhook deliveries and replaying them with a modified header is straightforward (e.g., via a proxy/logging endpoint that intercepts the delivery to their own shop before forwarding, or simply by resending an intercepted request with curl).

### Recommendation
Bind the routing/tenant identity to the verified bytes: include the `shop-domain` (and ideally `topic`) header in the signable string used for HMAC verification, or otherwise cryptographically bind them (e.g., verify against a session or expected shop set by the host application before dispatch). At minimum, document and enforce that consumers must independently verify that `WebhookMetadata#shop` corresponds to a shop actually known/registered to the app before trusting the body for that tenant — since the library currently offers no such check itself.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and registers/receives a webhook for topic `orders/create`, capturing the raw body `B` and header `X-Shopify-Hmac-Sha256: H` (a valid HMAC of `B` computed with the app's shared secret).
2. Attacker crafts a new HTTP request to the app's webhook endpoint with:
   - `raw_body = B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because it only signs `B`)
   - `X-Shopify-Shop-Domain: victim.myshopify.com` (changed)
   - `X-Shopify-Topic: orders/create` (unchanged or attacker-chosen)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(raw_body)`: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and processes attacker-supplied order data as if it belonged to the victim's shop, corrupting/poisoning tenant-scoped state maintained by the host application.

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
