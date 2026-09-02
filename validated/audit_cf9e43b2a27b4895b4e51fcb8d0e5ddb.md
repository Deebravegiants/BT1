## Title
Webhook Shop-Domain Header Is Not Covered by HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` validates webhook authenticity using an HMAC computed over the raw request body only, but the `shop` value used to route/authorize the webhook to a tenant is taken from an HTTP header that is completely outside the HMAC's coverage. An attacker who controls one shop where the app is installed can capture a legitimately-signed `(raw_body, hmac)` pair generated for their own shop and replay it against the app's webhook endpoint while swapping the `x-shopify-shop-domain` (or `shopify-shop-domain`) header to point at a victim shop. `Utils::HmacValidator.validate` will still pass because it only re-derives the signature from `@raw_body`, and `Webhooks::Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-supplied) body belongs to the victim shop.

### Finding Description
The identity binding that should hold is:
`shop bound by HMAC == shop the handler is told to act on`

In `Webhooks::Request`: [1](#0-0) 
`shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, while: [2](#0-1) 
`to_signable_string` — the only thing `HmacValidator` verifies — returns just `@raw_body`. The header carrying tenant identity is never mixed into the signed payload.

`HmacValidator.validate` computes the signature purely from `to_signable_string`: [3](#0-2) 

`Registry.process` trusts the HMAC check and then forwards `request.shop` (the unauthenticated header) directly to the handler as the tenant identity for the webhook payload: [4](#0-3) 

Because the same `client_secret`/HMAC key is shared across every shop that has the app installed, any shop owner (including a malicious one) can legitimately receive real `(body, hmac)` pairs from Shopify for their own shop's events. Since the shop header sits outside the signed bytes, that same `(body, hmac)` pair remains valid when replayed with a different `x-shopify-shop-domain` value. This is exactly the "bytes verified versus bytes parsed"/"field acted on but not covered by the HMAC" class of bug called out in the prompt: the verified bytes (`raw_body`) diverge from the bytes actually used to select the tenant context (`shop` header).

### Impact Explanation
This breaks the tenant boundary the HMAC is meant to enforce: an attacker-controlled shop can forge webhook events that the host application will process as if they originated from and pertain to a different (victim) shop. Depending on how the host app's webhook handler uses `WebhookMetadata#shop` (e.g., to look up the victim's session/access token and apply the attacker-chosen body — orders, product updates, GDPR data-request payloads, etc.), this can lead to cross-tenant data corruption or processing under the wrong tenant's credentials/session — matching the "cross-tenant access" High-impact category.

### Likelihood Explanation
Exploitation requires the attacker to have an app installation on at least one shop (their own, or the app's dev/test store) in order to receive a validly-signed webhook body, and requires the host application to trust `WebhookMetadata#shop` for identifying the tenant of the payload — which is the intended and documented usage pattern of this library's webhook handler API. No access token, `client_secret`, or privileged account is needed beyond ordinary use of the app as an unprivileged merchant, so likelihood is realistic for any app that dispatches per-shop side effects from webhook handlers.

### Recommendation
Bind the shop domain into the signed material, or otherwise cryptographically tie the header to the verified payload, before trusting it for tenant routing — e.g., include the `shop` header value in `to_signable_string`, or independently verify that the shop the handler receives matches a shop for which the app holds a valid session/access token before acting on the webhook. At minimum, document that `request.shop` is unauthenticated and must be cross-checked by the host app against a known/authorized session before use.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers an event (e.g., updates a product) so Shopify sends a legitimately signed webhook: `raw_body = B`, `x-shopify-hmac-sha256 = HMAC(client_secret, B)`, `x-shopify-shop-domain = attacker-shop.myshopify.com`.
2. Attacker captures `B` and its HMAC.
3. Attacker sends a forged HTTP request directly to the app's webhook endpoint with the same `raw_body = B` and same HMAC header, but sets `x-shopify-shop-domain = victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `B` against the HMAC — validation succeeds.
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and processes attacker-controlled data under the victim shop's identity.

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
