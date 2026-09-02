## Finding

The Shopify webhook verification in `ShopifyAPI::Webhooks::Registry.process` cryptographically authenticates only the raw request body, yet exposes the `shop`, `topic`, `webhook_id`, and `api_version` fields to the host app's handler as if they were equally authenticated. Any internet user who can get *any* legitimately HMAC-signed webhook delivered to the app (e.g. by installing the free app on their own store) can replay that body with attacker-chosen `X-Shopify-Shop-Domain`/`X-Shopify-Topic` headers and the signature will still validate, letting them impersonate another merchant/tenant to the handler.

### Title
Webhook HMAC only signs the raw body while `shop`/`topic`/`webhook_id` headers are trusted unverified, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` computes/verifies the HMAC over the body alone [2](#0-1) . However, `Registry.process` uses the unauthenticated header-derived `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to build the `WebhookMetadata` that is handed to the app's handler as trusted identity data [3](#0-2) . The `shop` field is documented as "The shop domain of the webhook" for handler consumers [4](#0-3) , and the docs claim `process` "will verify the request did indeed come from Shopify" [5](#0-4) , implying the shop identity is authenticated when it is not.

### Finding Description
The identity binding broken is: **shop header claimed to the handler == shop that Shopify actually signed for**. Before the request: `request.shop` is attacker-writable, unauthenticated header text; the HMAC covers only `@raw_body`. After `HmacValidator.validate` succeeds: the code treats `request.shop` (and `topic`, `webhook_id`) as if they had been verified together with the body, because a single boolean gate (`Errors::InvalidWebhookError` on failure) is the only check before dispatch [6](#0-5) . Since only the body bytes are bound to the HMAC, an attacker who obtains one authentic (body, hmac) pair — trivially available by installing the app on their own store and receiving any webhook — can resend that exact body/hmac pair to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header naming a different, victim shop. The signature check still passes because it never inspected those headers.

### Impact Explanation
This is a cross-tenant identity confusion: the handler receives `WebhookMetadata#shop` claiming to be a victim shop while the HMAC only proves the body came from *some* real Shopify-signed webhook (the attacker's own). Any handler implementation that uses `data.shop` to look up/act on shop-scoped resources (session revocation, mandatory GDPR compliance webhooks like `shop/redact` or `customers/redact`, billing/subscription state, feature flags) can be made to act on the wrong tenant's data based on attacker-controlled input, i.e. cross-tenant access, which is one of the explicitly in-scope Critical impacts.

### Likelihood Explanation
Requires only an unprivileged capability: install the app (many Shopify apps have free/dev-store installs) to receive one legitimate signed webhook, then replay it with modified headers to the app's public webhook endpoint. No knowledge of `api_secret_key` or any privileged credential is required, matching the rules' unprivileged-internet-user constraint.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable string, or otherwise cryptographically bind them to the body before trusting them in `Registry.process`/`WebhookMetadata`, and update `docs/usage/webhooks.md` to stop asserting that `process` fully "verifies the request did indeed come from Shopify" for those fields, or require host apps to cross-check `shop` against their own store of installed shops before acting.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com`; trigger any registered topic (e.g. `orders/create`) so Shopify sends a legitimately signed webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid for `B`), `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Capture `B` and `H`.
3. Send a new HTTP request to the app's webhook endpoint with the same body `B` and header `H`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and, if desired, a different `X-Shopify-Topic`, e.g. `shop/redact`).
4. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only [2](#0-1)  and it matches `H`, so `Registry.process` proceeds and calls the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)` [3](#0-2) , even though Shopify never signed anything for `victim-shop.myshopify.com`.

### Citations

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
