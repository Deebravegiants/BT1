### Title
Webhook `shop` domain used to route/attribute events is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop` (and `topic`/`webhook_id`) values are read from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC and then trusts `request.shop` to attribute the webhook to a tenant. Because the header is not part of the signed material, anyone who can obtain one validly-signed webhook body (trivially available by installing the app on their own free/dev store) can replay that body to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header, causing the handler to process attacker-controlled data under a victim shop's identity.

### Finding Description
The HMAC binding is defined in `Utils::VerifiableQuery` and implemented for webhooks in: [1](#0-0) 

`hmac` decodes the `hmac-sha256` header, and `to_signable_string` returns `@raw_body` — nothing else. The `shop`, `topic`, `api_version`, and `webhook_id` accessors simply read the corresponding headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` verifies only the body-derived HMAC via `Utils::HmacValidator.validate`, then immediately builds `WebhookMetadata` from the unauthenticated `request.shop`: [3](#0-2) 

`Utils::HmacValidator.validate` confirms only that `to_signable_string` (i.e., the body) was signed with `Context.api_secret_key`; it says nothing about which shop sent it: [4](#0-3) 

The security-relevant equality that the library implicitly claims to have checked is:
`shop attributed to the event == shop that actually triggered/owns the signed payload`

What is actually checked is only:
`HMAC(secret, raw_body) == received_hmac`

Since `shop` is not part of `raw_body` or any other signed field, these two statements are independent. Any party who can obtain one real, validly-signed webhook body/HMAC pair for **any** shop (including their own store, which anyone can create for free) can re-POST that exact body+HMAC to the target app's public webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header for a victim shop's domain. `HmacValidator.validate` still returns `true` (the body/HMAC pair is genuinely valid), and `Registry.process` dispatches the handler with `shop: <victim's domain>`.

### Impact Explanation
This breaks the tenant isolation boundary the library is supposed to provide via webhook signature verification: an attacker without any access token, session, or leaked secret can make the app process arbitrary attacker-chosen data (the body of a webhook they legitimately received for their own store) under the identity of a different, victim shop. Depending on how the host application's `WebhookHandler` uses `data.shop`/`data.body` (e.g. updating local per-shop records, triggering `app/uninstalled` cleanup, syncing order/customer data, billing state, etc.), this enables cross-tenant data corruption or state confusion — one merchant's webhook traffic can be attributed to another merchant's tenant record. This matches the Critical "cross-tenant access" impact category: the library's own signature-verification API (`Utils::HmacValidator.validate` + `Webhooks::Request#shop`) gives host applications a false guarantee that the returned `shop` value is authenticated when it is not.

### Likelihood Explanation
High. Exploitation requires no credentials, no access token, and no knowledge of `client_secret`/`api_secret_key`: an attacker only needs (a) a free Shopify development/partner store on which they install the target app to legitimately receive one signed webhook for a topic of their choosing, and (b) the ability to send an HTTP POST to the app's public webhook endpoint with a modified `shop-domain` header — both trivially satisfied by any unprivileged internet user.

### Recommendation
Bind the `shop` value into the material that is HMAC-verified, or otherwise authenticate it independently of the caller-supplied header before it is trusted for tenant attribution. Concretely:
- Do not treat `Webhooks::Request#shop` as authenticated on its own; require host applications to cross-check it against a shop known via an established, already-verified session/webhook registration, or
- Extend `to_signable_string` (or add a second verification step) that incorporates the shop domain into the value that is HMAC-checked, matching Shopify's actual webhook delivery guarantees for the fields the app relies on, and document clearly in `Registry.process`/`WebhookMetadata` that `shop` is unauthenticated unless separately validated.

### Proof of Concept
1. Attacker installs the target Shopify app on their own (free) development store `attacker.myshopify.com`, subscribing to a webhook topic the app handles (e.g. `orders/create`).
2. Shopify delivers a legitimate webhook POST to the app's endpoint:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over body>`, `x-shopify-topic: orders/create`
   - Body: attacker-controlled JSON (attacker fully controls the order content on their own store).
3. Attacker captures this exact body and HMAC value (e.g. from their own server logs, a proxy, or a webhook debugging tool).
4. Attacker re-sends an HTTP POST to the same app webhook endpoint, keeping the body and `x-shopify-hmac-sha256` identical, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` object; `Utils::HmacValidator.validate` recomputes HMAC over `@raw_body` and it matches, so `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker JSON>, ...)`.
6. The host application's webhook handler now processes attacker-supplied data as if it originated from `victim-shop.myshopify.com`. [3](#0-2) [1](#0-0)

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
