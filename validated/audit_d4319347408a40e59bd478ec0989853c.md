### Title
Webhook HMAC covers only the request body, not the `shop-domain` header, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Registry.process` accepts the request as authentic whenever `Utils::HmacValidator.validate(request)` succeeds. Because the `shop` value that is handed to the app's webhook handler is read from the `x-shopify-shop-domain` header, which is never included in the signed bytes, the identity binding "shop the HMAC authenticates" == "shop delivered to the handler" does not hold.

### Finding Description
`HmacValidator.validate` recomputes an HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field with `OpenSSL.secure_compare`: [1](#0-0) 

For webhooks, `to_signable_string` is defined to return only `@raw_body`: [2](#0-1) 

but `shop` (and `topic`, `webhook_id`, `api_version`) are pulled straight from unauthenticated HTTP headers with no cryptographic tie to the HMAC: [3](#0-2) 

`Registry.process` validates the HMAC and then dispatches the handler using `request.shop` taken from that same unauthenticated header: [4](#0-3) 

Since all shops that install the app share the same `Context.api_secret_key`, any merchant who installs the app (an "unprivileged" install, e.g. a free development store) legitimately receives real webhooks from Shopify with a body and a correctly computed HMAC. That attacker-controlled shop can capture one such `(body, hmac)` pair and replay it directly to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` only re-derives the signature from the body, so the forged request passes validation, and `WebhookMetadata.shop` delivered to the handler is the victim's domain even though the payload never actually originated from, or was authorized by, the victim shop.

This is exactly the identity-binding gap called out as in-scope: "a field acted on but not covered by the HMAC" — here `shop` is acted upon (used to attribute/act on data for a tenant) but is outside the signed bytes.

### Impact Explanation
This enables cross-tenant data confusion/injection: a host application that trusts `WebhookMetadata#shop` to decide which merchant's records to create, update, or delete will process attacker-supplied webhook bodies under an arbitrary victim shop's identity. Depending on the handler, this can corrupt or fabricate data attributed to a shop the attacker does not control, which matches the "cross-tenant access" impact category.

### Likelihood Explanation
Moderate-to-high: the webhook endpoint is a public HTTP endpoint (that's its purpose), `api_secret_key` is shared across every shop that installs the app (no per-shop secret), and creating a free/trial Shopify development store to legitimately trigger a webhook and observe `(body, hmac)` requires no privileged access. Only the `shop-domain` header needs to be altered in the replayed request; no secret material needs to be known or brute-forced.

### Recommendation
Bind the shop identity into the signed material, or verify it out-of-band before trusting `request.shop`:
- Have `Registry.process`/the handler cross-check `request.shop` against the set of shops with an active, stored session/installation for this app before acting on the payload, rather than trusting the header alone.
- Alternatively/additionally, require callers to supply the expected shop when processing a webhook and reject mismatches, or use Shopify's webhook `X-Shopify-Webhook-Id` combined with a persisted mapping of expected shop per subscription, since the header itself cannot be made part of `to_signable_string` (it is not signed by Shopify).

### Proof of Concept
1. Attacker installs the target app on a shop they control (`attacker-shop.myshopify.com`), which shares the app's single `api_secret_key`.
2. Attacker triggers a real webhook (e.g. `orders/create`) on their own shop and captures the raw body `B` and Shopify-computed `X-Shopify-Hmac-Sha256` header `H` — both valid because `HmacValidator.validate` only checks `HMAC(secret, B) == H`.
3. Attacker sends a POST directly to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` succeeds (it only checks the body/HMAC pair), and `Registry.process` invokes the handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"` and `body == B`, even though the victim shop never sent this event: [4](#0-3)

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
