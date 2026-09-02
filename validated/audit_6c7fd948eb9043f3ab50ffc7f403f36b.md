### Title
Cross-tenant webhook spoofing via `shop-domain` header not covered by HMAC verification - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, but the `shop` value that the gem hands to the host application's handler for tenant identification is read from an HTTP header that is never included in the HMAC-signed material. This breaks the intended binding `HMAC(secret, body) proves shop == request.shop`, matching the report's bug class of "a field acted on but not covered by the HMAC."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is untouched by the signature: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature strictly from `to_signable_string` (i.e., the body) and the configured secret(s), with no reference to headers: [4](#0-3) 

Because `shop` is outside the signed envelope, `HMAC(secret, body)` remains valid regardless of which value is placed in the `shop-domain` header. Any party who can obtain one genuine `(body, hmac)` pair for a webhook addressed to their own shop — e.g. a malicious merchant who installs the app and lets Shopify deliver a real webhook to their own store, or anyone who can otherwise capture a valid webhook payload/HMAC — can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header. `Registry.process` will accept the HMAC as valid and pass the attacker-chosen `shop` straight to `handler.handle`, per the documented `WebhookMetadata#shop` contract: [5](#0-4) 

Host applications are expected to use `data.shop` to key into per-tenant storage (session/access-token lookup, DB record association, job enqueuing), as shown in the gem's own example: [6](#0-5) 

### Impact Explanation
This is a cross-tenant confusion vector: an attacker-controlled `shop` value, unauthenticated by the HMAC, is delivered to the app's business logic as if it were authenticated. Depending on how the host app uses `data.shop` (e.g., to look up or scope another merchant's stored access token/session, or to write data attributed to another shop), this can enable cross-tenant data injection or lead to acting under another tenant's identity — satisfying the "cross-tenant access" Critical impact category in scope.

### Likelihood Explanation
Exploitation requires the attacker to first obtain one legitimate `(raw_body, hmac)` pair, which is trivially available to any merchant who installs the app (Shopify delivers real signed webhooks to installer's own shop), and then to replay it to the app's public webhook endpoint with a forged `shop-domain` header. No secrets, tokens, or privileged access are required beyond normal, unprivileged app installation — an "unprivileged internet user" analog as required by the rules.

### Recommendation
Include the trusted identifying headers (`shop`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed material, or otherwise cryptographically bind `shop` to the verified payload before it is handed to the handler, so that a replayed/relabelled request cannot alter the tenant a webhook is attributed to.

### Proof of Concept
1. Attacker (merchant "attacker-shop.myshopify.com") installs the app and lets Shopify deliver a genuine webhook, capturing the raw body `B` and its valid `x-shopify-hmac-sha256` value `H` (computed by Shopify over `B` with the app's real secret).
2. Attacker replays the request to the app's registered webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged header into `request.shop`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only — this still equals `H`, so validation succeeds: [7](#0-6) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own shop, and any per-tenant logic keyed off `data.shop` is executed under the victim's identity.

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

**File:** docs/usage/webhooks.md (L12-18)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
