## Title
Webhook `HmacValidator` never covers the `X-Shopify-Shop-Domain` header, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while `shop` is read from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts `request.shop` to build the `WebhookMetadata` passed to the host app's handler. Because the header is never part of the signed payload, an attacker who can obtain one valid `(raw_body, hmac)` pair (e.g., from a webhook delivered to their own shop) can replay it with a forged shop-domain header, making the app process attacker-controlled webhook data under a victim tenant's identity.

### Finding Description
The binding that should hold is:

`shop_bound_by_hmac == shop_used_by_handler`

but in this gem it is:

`shop_used_by_handler = header("shop-domain")` (unauthenticated) while `hmac == HMAC(raw_body)` only (`to_signable_string` returns `@raw_body`, `lib/shopify_api/webhooks/request.rb:36-38`). The `shop-domain` header is read separately (`lib/shopify_api/webhooks/request.rb:20-23`) and is never included in the signed string.

`ShopifyAPI::Utils::HmacValidator.validate` recomputes the HMAC purely from `verifiable_query.to_signable_string` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) and compares it to the `hmac` field taken from the `hmac-sha256` header (`lib/shopify_api/webhooks/request.rb:10-13`). Nothing in this comparison touches `shop`.

`ShopifyAPI::Webhooks::Registry.process` then does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
(`lib/shopify_api/webhooks/registry.rb:190-199`)

So the only thing cryptographically proven is "this body byte-string was HMAC'd with `api_secret_key`" — it proves nothing about which shop it came from. `request.shop` is handed to the host app's `WebhookHandler#handle` as trusted, tenant-identifying data. [1](#0-0) [2](#0-1) [3](#0-2) 

### Impact Explanation
Every shop that installs an app using the same `client_secret`/`api_secret_key` (which is the app-wide, not per-shop, secret used to sign all webhooks for that app) can generate a legitimately-HMAC'd webhook payload for its own shop, then replay that exact body/hmac pair to the app's webhook endpoint while substituting the `shop-domain` header for a different, victim shop that also has the app installed. `Registry.process` will accept the HMAC as valid (it only checks the body) and will invoke the app's handler with `WebhookMetadata#shop` set to the victim's domain. Any app logic that uses `shop` to select which tenant's session/data/settings to mutate (a standard pattern, since this is exactly why `shop` is included in `WebhookMetadata`) will act on the wrong tenant using attacker-supplied body content — i.e., cross-tenant data confusion/corruption without needing the victim's access token or credentials. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is realistic for an unprivileged attacker: creating a Shopify development store, installing the target app on it, and triggering any subscribed webhook topic (e.g. a cheap, self-triggerable topic like `app/uninstalled` or `products/create` on their own store) gives them a fully valid `(raw_body, hmac)` pair signed with the app's shared secret. No access token, `api_secret_key`, or victim credentials are required — only a normal, free installation of the target app by the attacker on a store they control, which is the standard "unprivileged internet user" entry point for this gem.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signed content, or otherwise cryptographically bind the shop domain to the HMAC before trusting it. Since Shopify's actual webhook HMAC only covers the body by protocol design, the mitigation should live at the app/session layer: require callers to cross-check `request.shop` against a shop they already have a stored, previously-authenticated session/access token for before acting on webhook data, and document this requirement prominently for `Registry.process`/`WebhookHandler` consumers, rather than presenting `WebhookMetadata#shop` as an already-trusted, tenant-bound value.

### Proof of Concept
```ruby
# Attacker installs the target app on their own shop "attacker.myshopify.com"
# and receives a legitimately signed webhook, e.g. for topic "products/create":
raw_body = '{"id":1,"title":"whatever"}'
hmac = OpenSSL::HMAC.base64digest(OpenSSL::Digest.new("sha256"), APP_SECRET, raw_body)

# Attacker now replays the SAME body+hmac to the app's webhook endpoint,
# but swaps the shop-domain header to the victim's shop:
headers = {
  "x-shopify-topic" => "products/create",
  "x-shopify-hmac-sha256" => hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, unauthenticated
  "x-shopify-api-version" => "2024-01",
  "x-shopify-webhook-id" => "forged-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# Passes HMAC validation because to_signable_string only returns raw_body:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# Registry.process happily dispatches to the handler claiming shop == "victim-shop.myshopify.com"
ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle receives WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker-controlled)
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
