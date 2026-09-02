## Title
Webhook Shop-Domain Header Not Covered by HMAC Signature — Cross-Tenant Webhook Spoofing ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (tenant identifier) that the registry hands to application webhook handlers is taken from an unauthenticated HTTP header. The library's own HMAC check therefore validates *which secret produced the body*, but never binds that proof to *which shop the request claims to be from*. An attacker who can obtain any single valid `(raw_body, hmac)` pair — trivially available to them by installing the app on their own store and capturing one of their own legitimate webhook deliveries — can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header. `HmacValidator.validate` still returns `true`, and the registry dispatches the payload to the app's handler tagged with the attacker-chosen shop, breaking the binding `hmac_signed(body) == identity(shop)` that a webhook consumer implicitly relies on for tenant isolation.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`:

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

The `shop` accessor, used downstream to attribute the event to a tenant, is pulled straight from request headers with no cryptographic linkage to the signature:

```ruby
sig { returns(String) }
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [2](#0-1) 

`HmacValidator.validate` only checks the HMAC against `verifiable_query.to_signable_string`, i.e. the body — it never incorporates `shop`, `topic`, or `webhook_id`:

```ruby
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [3](#0-2) 

`Registry.process` treats a passing HMAC check as full authentication of the entire request, including the shop, and dispatches accordingly:

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [4](#0-3) 

Because the signature never covers `shop`, any valid `(raw_body, hmac)` pair remains valid under any `shop-domain` header value. This is exactly the class of defect described in the reference report: a field that is *acted on* (here, the tenant identifier used to attribute and process the webhook) is not covered by the integrity check that is presumed to authenticate the whole message, so two distinct identities collapse onto the same verified artifact.

### Impact Explanation
Any merchant who has installed the app (an "unprivileged" actor relative to other tenants) can capture one legitimate `(body, hmac)` pair from their own shop's webhook traffic and replay it directly to the app's public webhook endpoint with a forged `shop-domain` header naming a different, victim shop. `HmacValidator.validate` accepts it, and `WebhookMetadata#shop` reports the attacker-chosen victim domain to the application's handler. Any host application that uses `metadata.shop` to look up the shop's session/access token, scope data writes, or otherwise key tenant-specific logic (the intended and documented use of `WebhookMetadata`) will process attacker-controlled data under another tenant's identity — a cross-tenant integrity/confidentiality violation satisfying the "cross-tenant access" impact bar.

### Likelihood Explanation
The attacker only needs to be able to install the app (or otherwise trigger one webhook delivery to themselves) and send one arbitrary HTTP POST to the app's known webhook endpoint — no access token, `client_secret`, or privileged credentials are required, and no interaction with the victim is necessary. This is squarely reachable by an unprivileged internet user.

### Recommendation
Bind the header-derived identity fields into the HMAC-signable content, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the signature (e.g., include them in `to_signable_string`, or require the host app to separately verify that the shop in the webhook belongs to a session that was itself established through OAuth/HMAC-validated flows) so that a valid signature for one shop's payload cannot be replayed under a different shop's identity.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook delivery with body `B` and header `x-shopify-hmac-sha256: H` (a valid HMAC of `B` under the app's shared secret) and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker POSTs the same body `B` and same `hmac` header `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(B, secret) == H` — this still holds, so validation succeeds.
4. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, and the attacker-controlled body `B` is now processed by the host application as if it originated from `victim.myshopify.com`.

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
