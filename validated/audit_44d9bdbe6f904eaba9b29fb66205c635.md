### Title
Webhook `shop` (tenant identifier) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing via replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw HTTP body [1](#0-0) . The `Request#to_signable_string` method used for that HMAC computation returns **only `@raw_body`** — none of the `shopify-*` headers (topic, shop-domain, api-version, webhook-id) are part of the signed material [2](#0-1) . Yet `request.shop` (parsed straight from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header) is handed directly to the app's webhook handler as the tenant identifier via `WebhookMetadata` [3](#0-2)  and [4](#0-3) .

### Finding Description
The identity binding that should hold is:

`shop asserted to the handler (request.shop, from header)` == `shop that actually produced/authorized the signed bytes`

Because the HMAC only signs the raw body and not the shop-domain header, this equality is never enforced. The `api_secret_key` used to compute/verify the HMAC is the **app's** single secret, shared across every shop that has installed the app [5](#0-4) . Consequently, any body+HMAC pair that is valid for *some* shop is valid for *every* shop, because the HMAC computation has no shop-specific input at all.

An unprivileged user who controls a shop where the app is installed (e.g., they installed a free/trial version of the target app to their own store) will legitimately receive real, correctly-signed webhook deliveries (raw body + `x-shopify-hmac-sha256`) from Shopify. They can capture such a delivery and replay it to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still succeed (body and HMAC are untouched and valid) [6](#0-5) , but `request.shop` will now report the victim's domain, and the handler will process the event believing it originated from the victim tenant [4](#0-3) .

### Impact Explanation
This breaks tenant isolation: an attacker-controlled shop can forge webhook events (e.g., `app/uninstalled`, `shop/update`, `customers/redact`, or any custom topic the host app has registered) that the application will attribute to an arbitrary victim shop. Depending on how the host application's handlers use `data.shop` (e.g., to key session/data lookups, mark a shop uninstalled, trigger data deletion/redaction for compliance topics, or update per-shop billing/subscription state), this can cause cross-tenant data corruption or unauthorized state changes scoped to a shop the attacker does not own. This falls under "cross-tenant access," a Critical-impact category.

### Likelihood Explanation
Moderate-to-high: exploitation requires only that the attacker be able to install the target app on any shop they control (a normal, unprivileged action) and be able to send an HTTP POST to the app's publicly reachable webhook endpoint with an attacker-chosen header — no access token, secret, or privileged account is required. The victim's shop domain is commonly public/guessable (a `myshopify.com` subdomain).

### Recommendation
Bind the tenant identity into the signed material or otherwise re-verify it out-of-band:
- Include the `shop-domain` (and ideally `topic`, `webhook-id`) header values in the string that is HMAC-verified, e.g., have `Request#to_signable_string` incorporate `shop`/`topic`, and reject verification if any of the covered headers are altered.
- If the wire format cannot change (Shopify signs only the body upstream), have `Registry.process`/consumers cross-check `request.shop` against a shop that is independently known to be onboarded/authorized for that specific webhook subscription (e.g., match against the webhook's known destination or the shop's stored session) before invoking the handler, rather than trusting the header value verbatim.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` (legitimate, unprivileged action).
2. Shopify sends a legitimately signed webhook to the app, e.g. body `{"id":1}"` with header `x-shopify-hmac-sha256: <valid-hmac-of-body>` and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures this raw body + HMAC header pair.
4. Attacker POSTs the identical raw body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC [2](#0-1) ; `Registry.process` proceeds and calls the handler with `shop: "victim.myshopify.com"` [3](#0-2) .
6. The host application's handler executes shop-scoped logic (e.g., uninstall cleanup, data deletion, subscription updates) against `victim.myshopify.com`, even though the victim never sent or authorized this webhook.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
