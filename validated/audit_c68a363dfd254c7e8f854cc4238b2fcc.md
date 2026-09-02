### Title
Webhook shop/topic identity spoofing due to HMAC covering only the raw body, not the `shop-domain`/`topic` headers - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body alone, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `ShopifyAPI::Webhooks::Registry.process` are all read from unauthenticated HTTP headers. Because the app's client secret (`api_secret_key`) is a single value shared across every merchant that has installed the app, any merchant who legitimately receives a webhook delivery for their own shop can replay that exact `(body, hmac)` pair to the app's public webhook endpoint while substituting an arbitrary `shop-domain`/`topic` header. The signature still validates (it never covered those headers), so the handler executes attributing the payload to a shop it never came from — a cross-tenant identity binding break.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` calls `verifiable_query.to_signable_string` and HMAC-compares it against the `hmac` header: [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only the raw JSON body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from caller-supplied headers with no cryptographic binding to the signed body: [3](#0-2) 

`Registry.process` trusts these header-derived values directly to dispatch the handler and to populate `WebhookMetadata`, the only mechanism through which the consuming app learns "which shop this event is for": [4](#0-3) 

The identity binding that should hold is: `hmac == HMAC(secret, body)` **and** `shop header == shop that produced body`. In reality only the first half is enforced — the gem verifies "bytes verified" (the body) but never binds it to "the shop asserted" (the header), matching the documented gap ("a field acted on but not covered by the HMAC").

Because `api_secret_key` is one shared value across all shops that have this single app installed (it's the app's client secret, not a per-shop secret), an attacker who has legitimately installed the target app on their own store receives real webhook deliveries `(body_A, hmac_A)` signed with that same shared secret for their own shop's events. `hmac_A` is valid for `body_A` regardless of which `shop-domain`/`topic` header accompanies the request, since those headers are outside the signed content.

### Impact Explanation
An attacker (an ordinary merchant who installed the app — an "unprivileged internet user" with respect to any other tenant) can:
1. Capture a legitimate `(raw_body, hmac)` pair from a webhook Shopify sends them for their own shop.
2. POST that exact body and HMAC header to the app's public webhook endpoint, but set `shop-domain` (and/or `topic`) headers to a victim shop's domain / a different topic.
3. `HmacValidator.validate` passes because only the body is checked; `Registry.process` dispatches the handler with `shop: <victim shop>` and attacker-chosen `body`/`topic` combination.

This lets an attacker inject fabricated events "as" another tenant into the app's business logic (e.g., triggering `orders/create`, `app/uninstalled`, or billing-related webhook handlers with attacker-controlled body content attributed to a shop they do not own). Depending on what the host application does with webhook data keyed by `shop`, this is a cross-tenant data/state corruption path — meeting the Critical bar ("cross-tenant access") defined for this exercise.

### Likelihood Explanation
Requires only: (a) installing the target app on any Shopify store (something any internet user can do for a public app) to obtain one valid `(body, hmac)` sample, and (b) sending a single crafted HTTP POST to the app's known webhook URL with modified headers. No access to `api_secret_key`, access tokens, or privileged accounts is needed — the shared client secret indirectly "leaks" its signing capability to every installer through ordinary webhook delivery. This is directly reachable through the gem's own `Registry.process`/`Request` code path, not a misuse of undocumented behavior.

### Recommendation
Bind the header-derived identity into the signed content check, e.g.:
- Extend `VerifiableQuery`/`Request#to_signable_string` (or add a separate check in `Registry.process`) to require that `shop`, `topic`, and `webhook_id` be cryptographically tied to the delivery (for example, by validating them against Shopify's known webhook source, or documenting/enforcing that consuming apps must cross-check `request.shop` against the shop they expect to have subscribed that specific `webhook_id`).
- At minimum, treat `shop`/`topic`/`webhook_id` as opaque/unauthenticated hints only usable for routing, and require that any authorization-affecting logic in `WebhookMetadata` consumers re-derive/verify shop identity from a source that is covered by the HMAC or otherwise authenticated (e.g., cross-referencing an independently stored webhook registration ID → shop mapping) rather than trusting the header value directly.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, causing Shopify to send a real webhook delivery to the app's endpoint:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <HMAC_A>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - Body: `raw_body_A` (attacker fully controls the order content on their own store, e.g. crafts a specific line-item/customer payload)
2. Attacker resends the identical `raw_body_A` and `x-shopify-hmac-sha256: <HMAC_A>` to the same webhook endpoint but replaces the header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Request.new(raw_body: raw_body_A, headers: forged_headers)` builds successfully (per `lib/shopify_api/webhooks/request.rb`); `to_signable_string` is unchanged (`raw_body_A`), so:
   `HmacValidator.validate(request)` → `true` (per `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. `Registry.process(request)` (per `lib/shopify_api/webhooks/registry.rb:188-200`) invokes the registered handler with `shop: "victim-shop.myshopify.com"` and the attacker's `raw_body_A`, even though that payload never originated from `victim-shop`.

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

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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
