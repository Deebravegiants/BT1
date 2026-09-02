### Title
Webhook shop-domain identity is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook purely by validating an HMAC over the raw request body, but the `shop` identity that the app's handler uses to attribute the event to a tenant is taken from an unsigned HTTP header. This breaks the identity binding `bytes_verified == bytes_trusted`, analogous to the reported Sherlock issue where `checkOrder()` validated an order/nonce independent of the caller context that consumed it.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate_signature` computes/compares the HMAC exclusively over that signable string [2](#0-1) . The `shop` accessor, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of the signed content at all [3](#0-2) .

`Registry.process` validates the HMAC and then immediately forwards `request.shop` (the unsigned header) into `WebhookMetadata`, which is handed to the app's `WebhookHandler#handle` as the shop for that event [4](#0-3) . The gem's own docs confirm apps are expected to trust `data.shop` as "the shop domain of the webhook" and use it to route work per-tenant (e.g., `perform_later(shop_domain: data.shop, ...)`) [5](#0-4) .

Because the HMAC secret (`api_secret_key`, i.e., the app's `client_secret`) is shared across every shop that installs the app, any shop that installs the app can receive a legitimately-signed webhook (Shopify computes `HMAC(raw_body, client_secret)` for that shop's own event) and observe a valid `(raw_body, hmac)` pair. Since the shop-domain header is excluded from the signed content, that same valid `(raw_body, hmac)` pair can be replayed to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to name a different, victim shop that also uses the app. `HmacValidator.validate` will still accept it because it only checks the body [6](#0-5) , yet the app's handler will process/attribute the event as belonging to the victim shop.

This mirrors the H-4 pattern precisely: verification (`_useNonce`/HMAC check) operates on one artifact (order nonce / raw body) while a materially different field consumed by the calling logic (auction shop routing / tenant shop) is left unchecked, letting an unprivileged actor (any shop that installs the multi-tenant app) desynchronize the two.

### Impact Explanation
This is a cross-tenant identity-confusion vector: an attacker who installs the app on their own (attacker-controlled) shop can forge the `shop` field seen by the app for webhook processing while keeping a cryptographically valid signature. Depending on what the host app does with `data.shop` (e.g., looking up the victim's stored offline session/access token by shop name as shown in `SessionUtils.offline_session_id` [7](#0-6) , triggering per-shop side effects, or writing attacker-controlled body data into a victim's tenant-scoped records), this can enable cross-tenant data corruption or actions being performed under a victim shop's identity/access token — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Requires only that the attacker be able to install the target app on a shop they control (a normal, unprivileged action available to any Shopify merchant/developer) and be able to send an HTTP request to the app's public webhook callback URL with a modified header — no access to `api_secret_key`, tokens, or victim credentials is needed.

### Proof of Concept
1. Attacker installs the vulnerable app on their own shop `attacker.myshopify.com`.
2. Attacker triggers an event (e.g., `orders/create`) on their own shop, causing Shopify to POST a webhook to the app: body `B`, header `shopify-hmac-sha256: HMAC(B, client_secret)`, header `shopify-shop-domain: attacker.myshopify.com`.
3. Attacker intercepts/replays this exact request to the app's webhook endpoint but changes only the `shopify-shop-domain` header to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#hmac`/`#to_signable_string` still validate successfully (`Registry.process` line 190) because the signature only covers `B`.
5. `Registry.process` calls the app handler with `WebhookMetadata(shop: "victim.myshopify.com", body: B, ...)`, and the app treats attacker-supplied data `B` as belonging to `victim.myshopify.com`. [4](#0-3) 

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the signed content that `HmacValidator` verifies, or independently verify that the `shop` header corresponds to a shop that is actually associated with the currently registered webhook/session before dispatching to the handler. At minimum, document prominently that `data.shop` from `WebhookMetadata` is unauthenticated and must not be trusted for tenant-scoped authorization decisions without additional verification (e.g., cross-checking against a known/registered shop list) — otherwise, mandate binding it into the signature.

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

**File:** docs/usage/webhooks.md (L12-29)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```

**File:** lib/shopify_api/utils/session_utils.rb (L63-66)
```ruby
        sig { params(shop: String).returns(String) }
        def offline_session_id(shop)
          "offline_#{shop}"
        end
```
