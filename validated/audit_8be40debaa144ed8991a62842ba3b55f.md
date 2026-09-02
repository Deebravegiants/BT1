### Title
Webhook `shop` attribution is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but it dispatches the webhook to the app's handler using the `shop` value read from the `X-Shopify-Shop-Domain` header — a field that is never included in the signed content. This breaks the binding "shop authenticated == shop the payload is attributed to," enabling a webhook that is validly signed for one tenant to be replayed with a different `shop-domain` header and be processed by the app as if it came from another shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all pulled straight from HTTP headers, none of which are part of the signed material: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` handed to the app's handler, with no cross-check that the `shop` header is consistent with anything covered by the signature: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` compute the HMAC purely from `verifiable_query.to_signable_string` (the raw body) and the app's `api_secret_key`: [4](#0-3) 

Because `shop-domain` is outside the HMAC scope, `(hmac, raw_body)` pairs are valid regardless of what `shop-domain` header accompanies them. Any party who can obtain one legitimately-signed `(raw_body, hmac)` pair — trivially achievable by installing the same app on their own store and capturing a real webhook delivery — can resend that exact body/HMAC to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` value. `Registry.process` will accept the HMAC (it never depended on the shop header) and hand the attacker-labeled `shop` straight to the handler as if the payload originated from that other tenant.

This is the exact analog of the reported bug class: a field acted upon (`shop`) is not covered by the integrity check (HMAC over `raw_body` only), so the identity binding `shop-authenticated == shop-attributed-to-data` does not hold.

### Impact Explanation
This yields cross-tenant data confusion: any handler logic keyed off `WebhookMetadata#shop` (e.g., persisting orders/products/customers per shop, triggering per-shop side effects, updating local tenant records) can be made to attribute attacker-supplied (but validly-signed-for-a-different-shop) payload content to an arbitrary victim shop domain. Depending on the host application's handler implementation, this can corrupt another merchant's data store, trigger unwanted actions against a victim tenant, or be used as a building block for further cross-tenant compromise — matching the "cross-tenant access" Critical-impact category, since the boundary between one merchant's webhook stream and another's is not actually enforced by this gem.

### Likelihood Explanation
Exploitation requires only unprivileged capabilities: the attacker installs the same third-party app on a store they control (or otherwise legitimately triggers one webhook delivery), captures the raw body and its HMAC header from that delivery, and replays it to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header. No access token, `client_secret`, or privileged account is required — only network access to the app's already-public webhook receiving endpoint, which is by design unauthenticated aside from the HMAC check this gem performs.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the material that is authenticated, or otherwise assert that the shop the app expects to receive a webhook for corresponds to a shop known to have installed the app before trusting the header value. At minimum, `Webhooks::Registry.process` should not treat `request.shop` as authenticated purely because the body HMAC validated; the library should document/enforce that host applications verify `request.shop` against a known, currently-installed shop record before acting on webhook contents, and ideally the gem should not expose `WebhookMetadata#shop` as though it were part of the verified payload without this caveat made structurally explicit (e.g., separating "signed" fields from "header-only, unauthenticated" fields in the API).

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g., `orders/create`) so Shopify delivers a request with a valid `X-Shopify-Hmac-Sha256` computed over the JSON body using the app's real `api_secret_key`.
2. Capture the raw body `B` and the HMAC header `H` from that delivery.
3. Resend an HTTP request to the app's webhook endpoint with the same body `B` and header `H`, but set `X-Shopify-Shop-Domain: victim.myshopify.com` (and any topic header desired).
4. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against `H` — the `shop-domain` header is irrelevant to that computation (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. The registered handler is invoked with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, even though the payload content actually originated from `attacker.myshopify.com`'s webhook delivery.

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
