### Title
Webhook `shop-domain` is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` validates webhook authenticity by computing an HMAC over the raw request body only, while the `shop` identity used to route and process the webhook is read from an unsigned HTTP header. An attacker who can obtain one genuine, HMAC-signed webhook (e.g., delivered to their own shop that has the app installed) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with a victim shop's domain. `Utils::HmacValidator` will still accept the request as valid because the header is not part of the signed payload, so the app's webhook handler executes attacker-controlled webhook data attributed to a shop the attacker does not control.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is excluded from the signed string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC purely over `to_signable_string` (i.e., the body) and compares it to the `hmac` header value; it never incorporates the shop header into the signed material: [3](#0-2) 

`Registry.process` accepts the request once `HmacValidator.validate` passes, and then forwards `request.shop` directly (unauthenticated with respect to the signature) to the handler as the identity of the shop that triggered the event: [4](#0-3) 

The broken identity binding is:
`shop asserted by HMAC-signed payload` ≠ `shop used by handler (`WebhookMetadata#shop`) to attribute/act on the event`

Because the app's `client_secret`/webhook shared secret is the same across all shops that install the app, any shop that has the app installed can capture a legitimately-signed webhook (body + `hmac-sha256` header) delivered to it, and resend that exact body/HMAC to the app's webhook endpoint with the `shopify-shop-domain` header swapped to an arbitrary victim shop domain. The signature still validates because the shop header was never part of the signed content.

### Impact Explanation
This breaks the tenant boundary the app relies on: a webhook event can be attributed to any shop merely by changing an unsigned header, while the signature check gives the illusion that both the body and the shop are trustworthy. Any app logic in the `WebhookHandler#handle` implementation that trusts `data.shop` to scope database writes, subscription/entitlement changes, or PII deletion (e.g., `shop/redact`, `customers/redact`, `customers/data_request` mandatory topics) can be triggered for a victim shop using attacker-controlled body content. This is cross-tenant impact.

### Likelihood Explanation
Exploitation requires only: (1) attacker's own shop to have the app installed so a legitimate webhook is delivered to them (an ordinary, unprivileged action available to any merchant), and (2) knowledge of a victim's shop domain, which is public (`*.myshopify.com`). No access to the app's `client_secret`, access tokens, or any privileged account is needed. The attack is a straightforward header substitution on a captured, valid request.

### Recommendation
Bind the shop identity into the verified material, e.g., include the `shopify-shop-domain` header (and ideally `topic`/`webhook-id`) in the HMAC-signed string, or independently verify that the shop header matches an expected/registered shop for that webhook subscription before dispatching to the handler. At minimum, document and enforce that `request.shop` must not be trusted unless it is cryptographically bound to the signed payload.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers/receives a legitimate webhook, e.g. `customers/redact`, capturing:
   - raw body `B`
   - header `shopify-hmac-sha256: H` (valid HMAC of `B` under the app's shared secret)
   - header `shopify-shop-domain: attacker.myshopify.com`
2. Attacker resends the same `B` and `H` to the app's public webhook endpoint but changes the header to `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H`, so validation passes: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to act on `victim.myshopify.com` using attacker-supplied body content, despite the victim never sending this webhook.

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
