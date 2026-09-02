### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook only by checking that the HMAC signs the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values, which are taken from HTTP headers and passed to the host application's handler as trusted metadata, are never included in the signed payload. An attacker who can obtain any single genuine `(raw_body, hmac)` pair — for example, an unprivileged merchant who has installed the app on their own shop and can observe/replay any webhook delivery Shopify sends them — can resend that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` (and/or topic) header value. The HMAC check still passes because it never covered those headers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are derived purely from headers, with no cryptographic link to the signed body: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the metadata handed to the app's handler: [3](#0-2) 

The identity binding that should hold is: `hmac == HMAC(secret, body ++ shop ++ topic ++ webhook_id)`, i.e. the shop/topic the app acts on should be the same shop/topic Shopify actually signed. Instead the gem only checks `hmac == HMAC(secret, body)`, so `shop`/`topic`/`webhook_id` are asserted-but-unverified fields, exactly the "field acted on but not covered by the HMAC" class of bug. Because the `hmac-sha256` value is computed exclusively over the raw body server-side by Shopify, any two webhook deliveries that happen to carry byte-identical bodies (which is common — e.g. `{}` bodies, or any webhook payload an attacker can produce verbatim on their own shop) will have colliding valid HMACs regardless of which shop or topic header accompanies them.

### Impact Explanation
This breaks the shop-identity binding across tenants: the host application's webhook handler is told `data.shop = <attacker-chosen value>` and `data.topic = <attacker-chosen value>` even though the cryptographic signature only vouches for the body content, not the shop or topic. Any host application logic that trusts `WebhookMetadata#shop`/`#topic` from a "validated" webhook (e.g. to look up which merchant's stored access token/session to act on, to mark a shop as uninstalled/redacted, or to route body data into a particular tenant's records) can be tricked into performing that action against a shop it was never intended for — a cross-tenant confusion. This matches the report's "Critical - cross-tenant access" category since the shop binding used for tenant identification is not covered by the authentication primitive that is supposed to protect it.

### Likelihood Explanation
Exploitation requires only a body+HMAC pair that Shopify signed for *some* installation of the app — trivially obtainable by any unprivileged merchant who installs the app on their own store and captures one webhook delivery (or triggers a webhook with a predictable/empty body such as `{}`). No access to `client_secret`, access tokens, or the target shop's credentials is required, satisfying the unprivileged-internet-user threat model.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string (or otherwise cryptographically bind them, e.g. by having the handler independently verify `request.shop` matches a shop with a known active installation before trusting it), so the HMAC check enforces that the shop/topic asserted by the headers matches what Shopify actually signed for this specific delivery.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and lets Shopify deliver a real webhook, e.g. `orders/create` with an empty or attacker-controlled JSON body `{}` and a valid `X-Shopify-Hmac-Sha256` header computed by Shopify over that exact body using the app's `client_secret`.
2. Attacker resends the identical raw body and HMAC header to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com` (and optionally changes `X-Shopify-Topic` to `shop/redact` or another sensitive topic that also has an empty/predictable body).
3. `Utils::HmacValidator.validate(request)` in `Registry.process` succeeds because it only checks `HMAC(secret, raw_body)`, which is unchanged. [4](#0-3) 
4. The registered handler receives `WebhookMetadata` claiming the event is for `victim-shop.myshopify.com`, and the host application acts on that spoofed shop identity.

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
