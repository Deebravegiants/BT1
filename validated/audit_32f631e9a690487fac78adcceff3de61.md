## Title
Webhook HMAC does not cover the shop-domain (or topic/webhook-id) header, enabling cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from HTTP headers that are never included in the HMAC-protected content. `ShopifyAPI::Utils::HmacValidator.validate` only checks that the body's HMAC matches, so any request whose body+HMAC pair is valid will be accepted regardless of what shop-domain header accompanies it, letting an attacker attribute webhook data to a shop it did not actually come from.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` and exposes `shop`, `topic`, `api_version`, and `webhook_id` purely from headers: [1](#0-0) [2](#0-1) [3](#0-2) 

`to_signable_string` returns only `@raw_body`, which is the sole input to the HMAC check in `HmacValidator.validate_signature`: [4](#0-3) 

`Registry.process` validates only this body HMAC, then constructs `WebhookMetadata` directly from the unauthenticated `shop-domain` header and passes it to the app's registered handler: [5](#0-4) 

The broken identity binding is: `hmac_verified(raw_body) != shop_attributed_to_handler`. Shopify signs webhook payloads with `HMAC(api_secret_key, raw_body)` — the same shared secret is used for every shop under the same app, and the signature depends only on the body bytes, not on which shop sent it. Consequently, once an attacker legitimately installs the app on their own shop (a normal, unprivileged action available to any Shopify merchant for a publicly listed app) and receives one authentic webhook delivery (raw_body + valid `X-Shopify-Hmac-Sha256`), they can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header with an arbitrary victim shop's domain. `Utils::HmacValidator.validate` will still return `true` because it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (forged) victim shop, topic, and webhook id, alongside the attacker-controlled body content.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: the shop identity delivered to the app's webhook handler is not the shop that the cryptographic signature actually vouches for. Any host application that follows this gem's documented flow — trusting `WebhookMetadata#shop`/`#topic` to look up or mutate per-shop state (e.g., session revocation on `app/uninstalled`, order/customer data ingestion, GDPR webhooks) — can be made to process attacker-supplied body content under another merchant's identity, which is a cross-tenant access scenario reachable by an unprivileged app-installing user, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Exploitation only requires: (1) ordinary installation of the target app on an attacker-controlled shop to receive one genuine webhook body+HMAC pair (trivial for any publicly available app), and (2) sending an HTTP POST to the app's webhook endpoint with the captured raw body/HMAC but a forged shop-domain (and optionally topic/webhook-id) header — no access to `api_secret_key`, tokens, or the victim's credentials is needed. This is a straightforward request-forgery once a single valid signed payload has been observed.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`/`api-version`) header values in the HMAC-signed content — or otherwise cryptographically bind them to the payload — so that `to_signable_string` covers everything `Registry.process` subsequently trusts. At minimum, `WebhookMetadata#shop` should never be derived from data outside the HMAC's protected scope.

### Proof of Concept
1. Install the target Shopify app on attacker-owned shop `attacker.myshopify.com`; capture one genuine webhook delivery, e.g.
   ```
   POST /webhooks HTTP/1.1
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-for-body>
   X-Shopify-Shop-Domain: attacker.myshopify.com
   X-Shopify-Webhook-Id: wh-1

   {"id":1,...attacker-controlled order payload...}
   ```
2. Replay the identical body and `X-Shopify-Hmac-Sha256` value, but change `X-Shopify-Shop-Domain` to `victim.myshopify.com` (and, if desired, the topic/webhook-id).
3. `ShopifyAPI::Webhooks::Request#hmac`/`#to_signable_string` still validate against the unmodified body (`lib/shopify_api/webhooks/request.rb:10-38`), so `Utils::HmacValidator.validate` returns `true`.
4. `ShopifyAPI::Webhooks::Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the cryptographic signature only ever vouched for the body, not for `victim.myshopify.com`.

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
