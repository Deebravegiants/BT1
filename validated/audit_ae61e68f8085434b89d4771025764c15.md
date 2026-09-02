## Title
Webhook HMAC signature does not cover the `shop-domain` and `topic` headers, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authorizes a webhook solely by validating an HMAC over the raw request body, then trusts the `shop-domain` and `topic` HTTP headers — which are *not* part of the signed material — to route the payload to a handler and to populate the `shop` field of `WebhookMetadata` passed to the app's business logic.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the HMAC purely over that signable string: [2](#0-1) 

`Registry.process` checks this HMAC first, then immediately trusts `request.topic` and `request.shop`, both sourced directly from unauthenticated headers (`shopify-topic`/`x-shopify-topic`, `shopify-shop-domain`/`x-shopify-shop-domain`): [3](#0-2) [4](#0-3) 

The identity binding that should hold is:
`HMAC(client_secret, raw_body) == received_hmac` **and** `shop header == shop that the signed body actually originated from`.

In this implementation only the first half is enforced. Since a single app's `client_secret` is shared across every shop that installs the app, any shop that has installed the app can legitimately trigger a webhook (with a body of the attacker's choosing, for a topic of the attacker's choosing) and receive a validly-signed payload from Shopify for their own store. The attacker (running their own dev/proxy shop, an "unprivileged internet user" with respect to the victim tenant) can then intercept the delivery to their own endpoint, swap the `shopify-shop-domain` header to the victim shop's domain (and/or the `shopify-topic` header), and forward it to the same app instance's webhook endpoint. Because `to_signable_string` never includes these headers, `HmacValidator.validate` still succeeds, and `Registry.process` builds a `WebhookMetadata` claiming the payload is for the victim shop: [5](#0-4) 

### Impact Explanation
The app-provided `WebhookHandler` receives `shop: request.shop` believing it has been authenticated together with the body, when in fact it was never covered by the signature. Any handler that keys persistence, cache invalidation, GDPR/redact actions, or entitlement changes off `WebhookMetadata#shop` can be made to act on a shop the attacker does not own — this is a cross-tenant access primitive (an attacker's own legitimately-triggered webhook is relabeled to affect another merchant's tenant data in the host application). This meets the Critical bar of "cross-tenant access" achieved purely through this gem's own webhook verification logic, without needing the app's `client_secret`, TLS interception, or a privileged account — only ability to trigger a webhook from one's own installed instance and replay/modify the forwarded HTTP request to the app's public webhook endpoint.

### Likelihood Explanation
Any developer/merchant who installs the target app on their own store can trigger arbitrary webhook topics that write attacker-chosen JSON bodies (e.g. `orders/create`, `customers/update`) and obtains a validly HMAC-signed delivery from Shopify. Relaying that delivery to the app's own public webhook endpoint with a modified `shop-domain`/`topic` header requires no secret material — only intercepting/replaying one's own webhook HTTP call, which is standard "attacker observes/modifies/replays traffic" capability, directly analogous to the reported bug class (an identity field acted upon that is not bound by the cryptographic check).

### Recommendation
Bind `shop`, `topic`, `api_version`, and `webhook_id` into the signed material (or otherwise cryptographically bind them, e.g. via a signed metadata envelope), or at minimum require callers to independently verify that the `shop-domain` header corresponds to a shop session/tenant the app already trusts before dispatching to handlers. `HmacValidator.validate` should not be treated as verifying anything beyond body integrity; `Registry.process` must not rely on unauthenticated headers for tenant routing.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers any webhook topic registered by the app (e.g. update a customer) causing Shopify to POST a validly HMAC-signed webhook to the app's public webhook endpoint, with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: customers/update`, `X-Shopify-Hmac-Sha256: <valid hmac of raw_body>`.
3. Attacker intercepts this outbound delivery (e.g. by pointing the app URL at infrastructure they control, or replaying the captured request) and rewrites `X-Shopify-Shop-Domain` to `victim.myshopify.com`, leaving `raw_body` and the HMAC header untouched.
4. Attacker sends the modified request to the same app's webhook endpoint.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)` — line 190 of `registry.rb` — which succeeds because it only checks `raw_body` against the HMAC.
6. The handler is invoked with `WebhookMetadata.new(topic: "customers/update", shop: "victim.myshopify.com", body: <attacker-controlled>, ...)`, causing the app to process attacker-controlled data as if it originated from the victim's shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
