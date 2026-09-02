This confirms the finding. The docs explicitly state `Registry.process` "will verify the request did indeed come from Shopify" (docs/usage/webhooks.md line 125), yet the HMAC verification only signs the raw body [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read from separate, unauthenticated headers [2](#0-1)  and then handed to the app's handler as trusted tenant identity in `WebhookMetadata` [3](#0-2) .

### Title
Webhook `shop`/`topic`/`webhook_id` headers are not covered by the HMAC, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify," but its HMAC check only authenticates the raw request body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` header values used to identify the tenant and dispatch the event are never included in the signed content, so they can be freely substituted by anyone who can also produce a genuine `(body, hmac)` pair for the same app.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `HmacValidator.validate` computes the signature purely from this `to_signable_string` value: [4](#0-3) . Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers with no HMAC coverage: [2](#0-1) .

`Registry.process` validates only the HMAC of the body and then constructs `WebhookMetadata` directly from these unauthenticated header fields, passing them to the app's handler as the trusted event identity: [3](#0-2) . The `WebhookMetadata` struct and its `shop`/`topic`/`webhook_id` fields are the gem's documented public contract for handlers (`docs/usage/webhooks.md`), and the docs explicitly promise the `process` call "will verify the request did indeed come from Shopify."

The broken identity binding, expressed as an equality that should hold but doesn't: `hmac_is_valid_for(raw_body) == hmac_is_valid_for(shop, topic, webhook_id, raw_body)`. Because only the body side of that equality is checked, an attacker who owns any shop that has the vulnerable app installed will receive genuine Shopify-signed webhooks for their own shop (valid HMAC computed by Shopify using the app's real `api_secret_key`, which the attacker never needs to know). They can capture one such `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header rewritten to name a different, victim shop. `HmacValidator.validate` still returns `true` because it never inspected those headers, and `Registry.process` will happily dispatch the forged event as if it originated from the victim shop.

### Impact Explanation
This lets an unprivileged app user (any merchant who has merely installed the app) inject webhook events that the host application will attribute to an arbitrary other tenant (shop). Since host apps are told (per the gem's own documentation) that `data.shop` reflects a verified, Shopify-originated request, they commonly use it to select which merchant record to update, refund, deauthorize, redact, etc. Forging events for `shop/redact`, `customers/redact`, `app/uninstalled`, or `orders/*` topics under an arbitrary victim shop identity constitutes cross-tenant access/manipulation — a Critical-severity impact per the given classification.

### Likelihood Explanation
Exploitation requires no privileged credentials, no knowledge of `api_secret_key`, and no access token — only that the attacker's own shop has the target app installed (a normal, self-service merchant action), after which they can freely replay/relabel a legitimately-signed webhook body against any topic/shop combination they choose, since the checked signature never binds those fields.

### Recommendation
Bind the tenant/topic identity into the authenticated content, e.g. by including `shop`, `topic`, and `webhook_id` in the HMAC-signed string (if Shopify's webhook signing supports this) or, at minimum, by having the gem cross-check `shop` against the shop associated with the specific `webhook_id`/subscription (via a stored mapping from webhook registration) before dispatching to handlers. Document clearly that `request.shop`/`request.topic` are NOT currently cryptographically authenticated by `HmacValidator.validate`, so host applications must independently verify tenant identity (e.g., against known installed shops) before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker installs the vulnerable app on their own shop, `attacker-shop.myshopify.com`, and registers a webhook (e.g., `customers/redact`).
2. Shopify sends a legitimate webhook to the app's endpoint:
   ```
   X-Shopify-Topic: customers/redact
   X-Shopify-Hmac-Sha256: <valid HMAC of raw_body computed with the app's real api_secret_key>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   X-Shopify-Webhook-Id: <id>
   Body: {"shop_id":123,"shop_domain":"attacker-shop.myshopify.com","customer":{...}}
   ```
   The attacker captures `raw_body` and the valid `hmac`.
3. The attacker resends the identical `raw_body`/`hmac` to the app's webhook endpoint, but changes only the header:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
4. `HmacValidator.validate` recomputes the HMAC over `raw_body` only and it matches, so `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(topic: "customers/redact", shop: "victim-shop.myshopify.com", body: ..., ...)` — as confirmed by `lib/shopify_api/webhooks/registry.rb:188-199`. Any host logic keyed on `data.shop` now acts on `victim-shop.myshopify.com` using attacker-supplied data, even though Shopify never sent this event for that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
