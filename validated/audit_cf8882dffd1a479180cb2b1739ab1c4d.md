Based on my analysis, I've confirmed a valid finding regarding the webhook `shop` identity binding not being covered by the HMAC signature.

### Title
Webhook `shop`, `topic`, `webhook-id`, and `api-version` are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic for a given `shop` once `Utils::HmacValidator.validate` succeeds, but the HMAC only ever signs the raw request body — never the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers that are trusted downstream as the tenant/event identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate_signature` computes/compares the HMAC solely against that signable string using the app's single, shop-independent `Context.api_secret_key` [2](#0-1) . `Registry.process` then extracts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` straight from unauthenticated headers and forwards them, unchanged, into `WebhookMetadata` passed to the app's handler [3](#0-2) . Those header accessors (`shop`, `topic`, `webhook_id`, `api_version`) are plain header reads with no cryptographic binding to the body or to each other [4](#0-3) .

This breaks the equality the gem implicitly relies on: `HMAC-verified(body)` == `shop the body is attributed to`. Because the same `api_secret_key`/`client_secret` is used to validate webhooks for every shop that has installed the app (there is no per-shop signing key), any actor who can install the app on their own store (an unprivileged, legitimately-created tenant) receives genuine webhooks with valid `x-shopify-hmac-sha256` values for arbitrary bodies they can influence (e.g. by editing their own shop's data to shape the webhook body). They can then replay that exact `raw_body` + valid HMAC while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`, `x-shopify-webhook-id`) to any other shop's domain, and `HmacValidator.validate` still returns `true` because it never inspects those headers.

### Impact Explanation
This is a cross-tenant data/authenticity confusion: the handler is told data came from shop B (`data.shop == "victim-shop.myshopify.com"`) and topic X, while both the payload and the cryptographic proof only ever attested to shop A's controlled bytes. Depending on how the host application uses `data.shop` (e.g., looking up a tenant's session/store, triggering per-shop side effects, writing to a shop-scoped record store as the docs' own example does — `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), this allows an attacker to inject attacker-chosen webhook bodies attributed to a victim shop, crossing the tenant boundary the gem is expected to enforce when it authenticates "this webhook is for `shop`". This matches the "field acted on but not covered by the HMAC" analog class in the report.

### Likelihood Explanation
Likelihood is bounded by the requirement that the attacker be an installed/authenticated tenant of the app (to receive a genuinely-signed webhook) and be able to shape at least the body bytes of some webhook topic they control (e.g., updating their own store's order/product/customer data to influence the JSON body, or simply replaying an unmodified body under a spoofed shop header if the handler doesn't inspect body contents for shop-specific fields). No secret material, TLS interception, or social engineering is required — only crafting and sending an HTTP POST with swapped headers to the app's public webhook endpoint.

### Recommendation
Bind the identity fields to the HMAC-covered material, or otherwise authenticate `shop`, `topic`, and `webhook_id` against server-side state rather than trusting the headers verbatim:
- Cross-check `request.shop` against the shop recorded for a known/registered subscription or webhook id (e.g., via a lookup keyed by `webhook_id` at registration time) before invoking the handler, instead of passing the raw header value through unchecked.
- At minimum, document/enforce that host applications must independently verify `shop`/`topic` consistency (e.g., against `sid`/session records) before trusting `WebhookMetadata#shop`, since `Registry.process` currently provides no such guarantee despite calling `HmacValidator.validate` first.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and registers for a webhook topic (e.g. `orders/create`) whose body they can influence by editing an order's note/attributes.
2. Shopify delivers a webhook to the app's endpoint with a genuine `x-shopify-hmac-sha256` computed over the JSON body using the app's `client_secret`, e.g. `{"id":1,"note":"<attacker payload>"}`.
3. Attacker captures this request and replays it to the same endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` identical, but replacing `x-shopify-shop-domain: attacker-shop.myshopify.com` with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `raw_body` [1](#0-0)  and succeeds since the body/HMAC pair is untouched.
5. The handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", body: {...attacker-controlled...})` [5](#0-4)  and processes attacker-controlled data as if it legitimately originated from the victim shop.

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
