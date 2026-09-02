## Title
Webhook shop identity spoofing via HMAC signature that only covers the request body, not the `shop-domain` header - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw HTTP body, but the `shop` value that is subsequently handed to the app's webhook handler is read from an unauthenticated HTTP header that the HMAC never covers. This breaks the identity binding `hmac_verified_bytes == shop_identity_attributed_to_the_event`, allowing any party who can obtain one valid `(body, hmac)` pair for the app (e.g. by legitimately installing the app on their own shop) to replay it while claiming to be a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is derived directly from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is never part of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (i.e. the raw body only) and compares it against the received signature using `Context.api_secret_key`: [3](#0-2) 

Once that check passes, `Registry.process` forwards `request.shop` — the unauthenticated header value — straight into `WebhookMetadata` and to the app's registered handler, which treats it as the authenticated tenant identity for the event: [4](#0-3) 

Because the app's `api_secret_key` is shared across *all* shops that install the app (it is not per-shop), any unprivileged developer can install the target app on their own store and receive a legitimately-signed webhook (many topics, e.g. `app/uninstalled`, ship with an empty or fixed body `{}`). The `(raw_body, hmac)` pair from that legitimate webhook remains valid for *any* value of the `shop-domain` header, since that header is not part of the signed bytes. The attacker can then replay the exact same body+HMAC to the app's public webhook endpoint while substituting a victim shop's domain in the header, and `Registry.process` will accept it as an authentic webhook "from" the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the gem asserts a webhook event belongs to shop X purely based on an unauthenticated header, while the only cryptographic guarantee it provides is "this body was signed by our client secret" (true for any tenant of the app). Any host application that uses `WebhookMetadata#shop` to select which tenant's data to act on (a documented, expected usage pattern — e.g. disabling/deleting a shop's stored session on `app/uninstalled`, or processing GDPR `customers/redact`/`shop/redact` compliance events) can be tricked into performing that action against an arbitrary victim shop rather than the attacker's own shop. This matches the "Critical - cross-tenant access" impact category, since it lets one tenant force the app to treat webhook data as belonging to a different tenant.

### Likelihood Explanation
Likelihood is high for any app that: (1) allows self-serve/public installation (most Shopify apps do), and (2) has at least one webhook topic with a static or attacker-known body (e.g. `{}` for `app/uninstalled`). No access to the victim's data, access token, or the app's `client_secret` is required — only a legitimate install of the target app on an attacker-owned shop, which is normal unprivileged usage.

### Recommendation
Bind the `shop` identity into the value that is verified, not just read from an unauthenticated header:
- Include the `x-shopify-shop-domain` header value (and ideally `webhook-id`/`api-version`) in the signable string that `HmacValidator` verifies, OR
- Compare the header-provided shop against an independently-verified source (e.g., look up the shop associated with the given `webhook_id` via the Admin API, or require the host app to cross-check `request.shop` against a shop it already has a stored, authenticated session for) before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` (ordinary, unprivileged action).
2. Attacker triggers/receives a legitimate webhook for a topic whose body is static/predictable, e.g. `app/uninstalled` with body `{}`. They capture the valid header `x-shopify-hmac-sha256: <HMAC over "{}">` computed with the app's real `api_secret_key`.
3. Attacker sends a forged HTTP POST directly to the app's public webhook endpoint:
   ```
   POST /webhooks
   x-shopify-topic: app/uninstalled
   x-shopify-hmac-sha256: <captured valid HMAC over "{}">
   x-shopify-shop-domain: victim-shop.myshopify.com
   x-shopify-webhook-id: <any>
   x-shopify-api-version: <any>

   {}
   ```
4. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) validates the HMAC successfully (it only checks the body `"{}"`), then invokes the app's `app/uninstalled` handler with `shop: "victim-shop.myshopify.com"`, causing the host app to act (e.g., delete stored session/data) as though the victim shop uninstalled the app.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
