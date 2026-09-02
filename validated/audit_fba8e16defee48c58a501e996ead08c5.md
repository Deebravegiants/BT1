This confirms the finding. The gem's documentation (`docs/usage/webhooks.md` line 125) explicitly promises that `Registry.process` "will verify the request did indeed come from Shopify," and the `data.shop` field is documented as "The shop domain of the webhook" (`docs/usage/webhooks.md` line 14) with no caveat that it is unauthenticated — so a host app relying on the gem's own guarantee is squarely in scope.

### Title
Webhook `shop` attribution is not covered by the HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook only by checking the HMAC over the raw request body. The `shop` value that identifies which merchant the webhook event belongs to is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header and is never included in the HMAC-covered content, so it is fully attacker-controllable independent of signature validity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is derived purely from a header and has no cryptographic link to the signed body: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which computes the signature only over `to_signable_string` (i.e., the body), then immediately trusts `request.shop` to build the dispatched `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The HMAC validator itself only ever signs/verifies the string handed to it by the `VerifiableQuery` interface — for webhooks that is the body, never the shop header: [4](#0-3) 

The binding that breaks is: **shop value verified by the HMAC (none) ≠ shop value used to key/attribute the webhook event (`request.shop`, taken from an unauthenticated header)**. The gem's own documentation tells host apps that `Registry.process` "will verify the request did indeed come from Shopify" and that `data.shop` is simply "The shop domain of the webhook" — i.e., it presents `shop` as trustworthy output of verification, when in fact it is not covered by the check at all (`docs/usage/webhooks.md` lines 14, 125).

### Impact Explanation
Any actor who can obtain one genuinely-signed webhook body+HMAC pair for their own tenant (which Shopify delivers to them merely by installing the app and triggering an event) can resend that exact body/HMAC combination while substituting an arbitrary `shopify-shop-domain` header. `Registry.process` will accept it as valid and dispatch a `WebhookMetadata` claiming the event belongs to any shop domain of the attacker's choosing, including a victim merchant's shop. Because the gem markets `shop` in `WebhookMetadata` as verified webhook data, apps built on this gem's documented contract will process and key data/actions against the forged shop, resulting in cross-tenant data or state confusion (e.g., writing attacker-supplied order/product data into the victim shop's records, or triggering shop-scoped side effects under the wrong tenant).

### Likelihood Explanation
Likelihood is high for any multi-tenant app built on this gem's documented webhook feature: the attacker only needs to be an ordinary, unprivileged merchant who has installed the app (no access to `api_secret_key`, no privileged account, no TLS interception). They passively receive one legitimate webhook to their own endpoint and replay it with a modified header — a trivial HTTP replay requiring no cryptography.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or otherwise cryptographically tie the shop-domain header to the signed payload before trusting it (e.g., require the host app to cross-check `request.shop` against a known/subscribed shop list, or include the shop domain in the signable string used by `HmacValidator`). At minimum, update documentation to explicitly warn that `shop` is unauthenticated and must be independently validated by the consuming app.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a subscribed event (e.g., `orders/create`). Shopify delivers a legitimate webhook to the app's endpoint:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of body B>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   Body: B
   ```
2. Attacker captures this request (it was delivered straight to their own server) and resends it to the same endpoint, only replacing the shop header:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same valid HMAC of body B>
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: B   (unchanged)
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only — it matches, so validation passes.
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)`, and the host app processes attacker-controlled data under the victim's tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
