This confirms the finding: the webhook `shop` field is documented as trustworthy (`docs/usage/webhooks.md` line 125: "This will verify the request did indeed come from Shopify") but it is not actually covered by the HMAC signature.

### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `webhook_id`, and `api_version` from unauthenticated HTTP headers, while the HMAC signature computed by `HmacValidator` only covers the raw request body (`to_signable_string` returns `@raw_body`). `Registry.process` treats a passing HMAC check as proof the whole request — including the `shop` header — "did indeed come from Shopify" (per `docs/usage/webhooks.md` line 125), then hands `request.shop` directly to the app's handler as an authenticated tenant identifier.

### Finding Description
`Utils::HmacValidator.validate` verifies `verifiable_query.to_signable_string` against the `hmac` value using `Context.api_secret_key`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw body — none of the identifying headers are part of the signed payload: [2](#0-1) 

`Registry.process` uses this single HMAC check as its sole authentication gate, then forwards the unauthenticated `request.shop` (and `topic`/`webhook_id`) straight into `WebhookMetadata`, which is delivered to the app's handler as trusted data: [3](#0-2) 

Because the api_secret_key is shared across every shop that installs a given app, any shop that has installed the app can capture one of its own genuine webhook deliveries (valid `raw_body` + `hmac` pair, since the HMAC only binds to body bytes). That captured request can then be replayed to the app's webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header rewritten to name a different, victim shop. The HMAC check still passes because the header is not part of the signed content, so `Registry.process` calls the handler with `data.shop` set to the attacker-chosen victim domain and `data.body` containing the attacker's own (crafted) resource data. This breaks the identity binding `hmac-verified bytes == shop the data is attributed to`, letting one tenant of a multi-tenant app inject data that the app processes as belonging to a different tenant.

### Impact Explanation
This is a cross-tenant identity confusion: a shop with no privileged access to a victim shop's data can cause the app to process/ingest arbitrary attacker-controlled webhook payloads (e.g., fake `orders/create`, `customers/update`, GDPR topics, etc.) under the victim's shop identity. Depending on what the host app's `WebhookHandler#handle` does with `data.shop`/`data.body` (e.g., write to the victim's records, trigger side effects scoped by `data.shop`), this can lead to cross-tenant data corruption or injection — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate installer of the target app (an "unprivileged internet user" relative to any other tenant of the same multi-tenant app) — no access token, secret, or privileged Shopify role is needed. Capturing one's own valid webhook body+HMAC and replaying it with a modified header is straightforward, since headers are never covered by the signature.

### Recommendation
Bind the identifying headers (`shop`, `topic`, `webhook_id`, `api_version`) into the signed material, or otherwise cross-check `request.shop` against an app-known set of subscribed shops before trusting it. At minimum, `HmacValidator`/`Webhooks::Request` should document loudly that `shop` is unauthenticated, and `Registry.process` (or its documentation) should not claim the whole request, including the shop header, is verified.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook: raw body `B` with header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the exact same `B`/`H` pair to the app's webhook endpoint but changes the header to `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#hmac` reads the unchanged `H`; `to_signable_string` returns the unchanged `B`; `Utils::HmacValidator.validate` succeeds (`lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. `Registry.process` calls the registered handler with `WebhookMetadata(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to treat attacker-controlled data as originating from `victim.myshopify.com`.

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
