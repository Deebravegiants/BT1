### Title
Webhook `shop` identity is not bound to the HMAC, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shop-domain` header as the tenant identity passed to the app's handler. Because the `shop` field is never included in the signed material, any holder of one valid `(body, hmac)` pair for the shared app `client_secret` can relabel that payload with an arbitrary victim shop domain and have it accepted as authentic.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read from the `shopify-shop-domain` / `x-shopify-shop-domain` header completely independently of the signed string: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which compares `HMAC(raw_body, api_secret_key)` against the received signature — the `shop` header plays no role in this check: [3](#0-2) [4](#0-3) 

Once the body-only HMAC passes, `request.shop` — an unauthenticated header value — is forwarded directly into `WebhookMetadata` and handed to the app's handler as the trusted tenant identifier: [5](#0-4) 

The identity binding that should hold is: `shop header == shop cryptographically bound by the HMAC`. Since the `client_secret` (and therefore the HMAC key) is shared across every shop that installs a given app, a valid `(body, hmac)` pair proves only "this came from a shop that installed this app," not "this came from shop X." An attacker who installs the app on their own store receives genuine, correctly-signed webhook deliveries. They can then replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim's domain. `HmacValidator.validate` still succeeds (it only checks the body), so `Registry.process` calls the app's handler believing the payload originates from the victim shop.

### Impact Explanation
This breaks the shop-authenticated-vs-shop-used-as-tenant-key binding and grants cross-tenant access: an unprivileged internet user (anyone who can install the app for free on their own store) can inject arbitrary, attacker-chosen webhook payloads (e.g., `orders/create`, `customers/update`, `app/uninstalled`) attributed to any other merchant using the same app, without ever obtaining that merchant's credentials. Depending on the host app's handler logic, this can corrupt or fabricate per-tenant data, trigger unauthorized business actions (e.g., simulate `app/uninstalled` to deprovision a victim tenant), or leak/overwrite tenant-scoped state — a Critical, cross-tenant impact per the scope's Critical bucket.

### Likelihood Explanation
Likelihood is high in any scenario where the vulnerable app is a public/multi-tenant app: obtaining one genuine `(body, hmac)` pair only requires installing the app once on an attacker-controlled shop (a normal, unprivileged action for any Shopify user), and then reusing it verbatim except for one header. No secret, token, or elevated privilege is needed.

### Recommendation
Bind the shop identity into the material that is HMAC-verified, or otherwise authenticate the header out-of-band, e.g.:
- Include `shop-domain` (and `topic`, `api-version`, `webhook-id`) in the signable string used by `HmacValidator`, matching them against what Shopify actually signs, or
- Cross-check `request.shop` against an app-side registry of shops that are known/authorized to have this app installed, and reject webhooks for unknown/unexpected shop domains before dispatching to handlers, or
- Require the host application to independently verify shop provenance for each webhook (e.g. against its own session store) before trusting `WebhookMetadata#shop` for tenant-scoped operations, and document this requirement clearly since the current library-level guarantee is insufficient.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, causing Shopify to send a legitimately signed webhook, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: app/uninstalled
   x-shopify-hmac-sha256: <valid HMAC of body B>
   x-shopify-shop-domain: attacker.myshopify.com
   Body: B = "{}"
   ```
2. Attacker replays the identical request to the app's webhook endpoint but changes only the shop header:
   ```
   POST /webhooks
   x-shopify-topic: app/uninstalled
   x-shopify-hmac-sha256: <same valid HMAC of body B>
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: B = "{}"
   ```
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(B, api_secret_key)` and matches the received signature — validation passes because the shop header is not part of `to_signable_string`.
4. The app's `app/uninstalled` handler is invoked with `shop: "victim-shop.myshopify.com"`, causing the host application to treat the victim's tenant as having uninstalled the app (or process any other forged topic/body pair against the victim's tenant data).

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
