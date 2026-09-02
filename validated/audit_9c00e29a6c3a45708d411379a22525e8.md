### Title
Webhook `shop-domain` header is trusted for tenant identity but not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop` (tenant identity) is read from an unauthenticated HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates only the body's HMAC and then forwards the unauthenticated `shop` header value to the app's handler as the trusted tenant identifier, even though the documentation states that `process` "will verify the request did indeed come from Shopify."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed string: [2](#0-1) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e., the raw body only) and compares it with `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` validates only this HMAC and then constructs `WebhookMetadata` directly from `request.shop` (the unauthenticated header), passing it to the app's handler as the trusted tenant identifier: [4](#0-3) 

The identity binding that should hold is:
`shop` value delivered to the handler == `shop` value cryptographically bound to the signed bytes (`raw_body` + secret).

In reality: `shop` header ≠ any HMAC-covered field. `WebhookMetadata.shop` is populated straight from `request.shop`, which is entirely attacker-controllable header data. [5](#0-4) 

Documentation instructs developers to trust `data.shop` as "The shop domain of the webhook" and states `process` "will verify the request did indeed come from Shopify": [6](#0-5) [7](#0-6) 

**Exploit path:** Any user who has a shop of their own (a merchant with the app installed, or anyone who can trigger a webhook event on any shop that has this app registered, e.g. via installing the app on a free development store) receives a genuinely-HMAC-signed webhook payload for that shop. Because the HMAC covers only `raw_body`, the same `(raw_body, hmac)` pair remains valid regardless of which `shop-domain` header value is sent. The attacker can then replay that exact `raw_body`/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never looks at the header), and the app's handler receives `WebhookMetadata` claiming the body originated from the victim shop, even though it did not.

### Impact Explanation
This breaks the tenant boundary the gem is documented to enforce ("verify the request did indeed come from Shopify" and provide "the shop domain of the webhook" to the handler). Applications that key persistence, deduplication, authorization, or side effects (e.g., "cancel order for shop X", "update inventory for shop X", billing/webhook counters, or feature-flag/eligibility state) off `data.shop` without independent verification will process attacker-chosen data as if it belongs to a different, victim tenant — a cross-tenant confusion/spoofing primitive. This matches the Critical "cross-tenant access" impact category, since the root cause is internal to this gem's `Request`/`Registry` design (the HMAC-signable content excludes the identity field the API contract promises is verified).

### Likelihood Explanation
Low complexity: any actor able to obtain one genuinely-signed webhook body (e.g., by installing the app on their own or a free development shop and triggering any subscribed topic) can replay it with an arbitrary `shop-domain` header value. No access to `api_secret_key`, tokens, or privileged accounts is required beyond being an ordinary merchant able to install the target app — which is the openly available onboarding path for any Shopify app. The library performs no cross-check between the header-derived `shop` and any signed content, and no code path in `Registry.process` or `Request` mitigates this.

### Recommendation
Bind the shop identity to the HMAC-verifiable content, or otherwise independently verify tenant identity before trusting `WebhookMetadata.shop`:
- Include the `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) in the HMAC-signable string alongside the raw body, and update `HmacValidator`/`Request#to_signable_string` accordingly (this would require a compatible change agreed with Shopify's webhook signing scheme, since Shopify signs only the body today).
- If the signing scheme cannot include the header, document explicitly (and ideally enforce in `Registry.process`) that consuming applications MUST cross-check `data.shop` against a shop that is known to have an active, registered webhook/session for that specific `webhook_id`/topic before trusting it, rather than presenting `shop` as an already-verified field.
- At minimum, update `docs/usage/webhooks.md` to remove the "verify the request did indeed come from Shopify" wording insofar as it implies the `shop` field is verified, since that overstates the guarantees provided by `Registry.process`.

### Proof of Concept
```ruby
# Attacker owns/controls "attacker-shop.myshopify.com" with the target app installed,
# and receives a real Shopify webhook there (any topic), giving them a valid (raw_body, hmac) pair.

raw_body = '{"id": 1, "note": "hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
# ^ This is exactly what Shopify would have sent for attacker-shop.myshopify.com

# Attacker replays the SAME body/hmac pair against the app's endpoint,
# but swaps the shop-domain header to the victim shop.
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, not covered by HMAC
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate succeeds (it only checks raw_body against the shared secret)
# => The app's handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", body: ...)
#    even though this payload never originated from victim-shop.
```

Note: I was unable to find any additional cross-check of `shop` against a stored/registered webhook subscription elsewhere in the library (e.g., in `Registry.process` or `WebhookHandler`), based on the code and tests available in the index. If such a check exists outside the indexed portions of the repo, it was not discoverable via search; a full-repository review via a Devin session would be needed to rule that out definitively.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
