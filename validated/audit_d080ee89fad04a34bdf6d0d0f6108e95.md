## Title
Webhook `shop-domain` header is trusted for tenant attribution without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

## Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying an HMAC computed over the raw request body, then trusts the unauthenticated `X-Shopify-Shop-Domain` header to attribute the webhook to a specific merchant/tenant. Because the shop identity is not part of the signed payload, an unprivileged attacker who legitimately installs the app on their own store (and therefore receives genuine, correctly-signed webhooks) can replay the exact same signed body while substituting an arbitrary victim shop domain in the header, and the library will report it to the app's handler as an authentic webhook "from" the victim shop.

## Finding Description
The identity binding that should hold is:

`shop attributed to a processed webhook == shop that Shopify actually sent it for`

`Utils::HmacValidator.validate` verifies the request only against `verifiable_query.to_signable_string`: [1](#0-0) 

For webhook requests, `to_signable_string` returns only the raw HTTP body — no header, including the shop identity, is included in the signed material: [2](#0-1) 

`shop` is read straight from an attacker-controllable HTTP header, independent of the HMAC: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately hands `request.shop` to the application's handler as trusted tenant data, with no additional check that the HMAC-verified body actually belongs to that shop: [4](#0-3) 

Because the `api_secret_key` used to sign webhooks is shared across every merchant that has installed the app (it is not per-shop), any merchant who installs the app can obtain a genuinely-signed `(body, hmac)` pair for their own shop. The equality that should be enforced ("the HMAC covers the shop this data is attributed to") does not hold before the fix, and after replay of the pair with a swapped `shop-domain` header, the two sides diverge: `HmacValidator.validate` reports success while `request.shop` returns an attacker-chosen victim domain.

## Impact Explanation
This crosses a tenant boundary: an unprivileged, non-victim merchant can cause the app to process attacker-controlled webhook data (topic + body) as if it originated from a shop they do not control. Depending on the handler logic wired up per the documented usage pattern, this can be used to inject or spoof data (e.g., fake `orders/create`, `customers/redact`, `app/uninstalled` events) attributed to a victim tenant, i.e. cross-tenant access/confusion, which the rules classify as Critical impact.

## Likelihood Explanation
The webhook endpoint is, by design, publicly reachable and unauthenticated apart from HMAC verification, exactly as documented in `docs/usage/webhooks.md`'s `Registry.process` example. All an attacker needs is: (1) install the target app on their own shop (a normal, unprivileged action), (2) capture one genuine webhook delivery (raw body + `hmac-sha256` header), and (3) resend that exact body/HMAC pair to the app's public webhook route with a modified `shop-domain`/`x-shopify-shop-domain` header. No secrets, tokens, or privileged access are required.

## Recommendation
- Include the shop identity (and other identifying context, e.g. topic, webhook id) in the data covered by the HMAC, or
- Require host applications to cross-check `request.shop` against records of shops that are actually expected to receive that specific `topic`/webhook subscription (e.g., validate shop exists in the app's own installed-shop store before trusting `WebhookMetadata#shop`), and document this requirement clearly and enforce it inside `Registry.process` rather than leaving it entirely to callers.
- At minimum, update `Registry.process`/`WebhookMetadata` to make explicit that `shop` is unauthenticated header data, not cryptographically bound to the verified body, and add a repository lookup or additional integrity check before dispatching to the handler.

## Proof of Concept
1. Attacker signs up for the target Shopify app on their own store `attacker.myshopify.com` and registers/receives a webhook (e.g., `orders/create`).
2. Shopify delivers a POST to the app's webhook endpoint with:
   - `x-shopify-hmac-sha256`: valid HMAC over the raw JSON body, computed with the app's `api_secret_key`.
   - `x-shopify-shop-domain`: `attacker.myshopify.com`.
   - Body: attacker-controlled order JSON (attacker crafts their own test order contents).
3. Attacker captures the raw body and the `x-shopify-hmac-sha256` value unchanged.
4. Attacker sends a new POST directly to the app's public webhook endpoint with the same body and HMAC header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `Utils::HmacValidator.validate` succeeds (it only checks the body against the HMAC), and `Registry.process` calls the topic handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, causing the app to treat attacker-supplied data as authentic for the victim tenant.

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
