### Title
Webhook `shop`, `topic`, and `webhook_id` are trusted from unsigned HTTP headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content from the raw body alone, while the tenant-identifying fields (`shop-domain`, `topic`, `webhook-id`, `api-version`) come from HTTP headers that are never included in the signed bytes. `Registry.process` verifies the HMAC and then unconditionally dispatches the handler using `request.shop`, so the binding "HMAC-verified bytes == bytes used to identify the tenant" is broken exactly like the Taurus `_decreaseCurrentMinted` bug, where the value checked (`currentMinted[account]`) was not the value actually mutated (`currentMinted[msg.sender]`).

### Finding Description
`to_signable_string` for `ShopifyAPI::Webhooks::Request` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, independent of the signed payload: [2](#0-1) 

`Registry.process` calls `Utils::HmacValidator.validate(request)`, which only proves the *body* was signed with the app's `api_secret_key`; it says nothing about which shop the body belongs to. Immediately after, the handler is invoked with `shop: request.shop` taken from the unauthenticated header: [3](#0-2) 

`HmacValidator.validate_signature` confirms this — it only ever compares `verifiable_query.to_signable_string` against the computed HMAC, so any field outside `to_signable_string` is unauthenticated: [4](#0-3) 

Because `api_secret_key` (the `client_secret`) is a single value shared by the app across every installing shop, any body that Shopify validly signs for the attacker's own store — for instance an `app/uninstalled` or GDPR compliance webhook delivered for a shop the attacker legitimately controls/installs the app on — carries a valid HMAC regardless of the `x-shopify-shop-domain` header value. Since that header is not part of the signed bytes, an attacker who owns a copy of one such request (from their own installation) can resend it to the app's fixed webhook endpoint with the `x-shopify-shop-domain` header changed to any other merchant's domain. `HmacValidator.validate` still returns `true` (the body/HMAC pair is genuinely valid), and `Registry.process` will hand `WebhookMetadata` for the *victim* shop to the app's handler.

This is the same identity-binding break as the report: the value verified (`accountMinted` on `account` / here, the HMAC over the raw body) is not the value the code actually acts on (`currentMinted[msg.sender]` / here, `request.shop` from the header).

### Impact Explanation
This allows cross-tenant webhook forgery: an attacker who legitimately installs the target app on their own (attacker-controlled) shop obtains a body+HMAC pair that Shopify itself signed. They can replay this content while spoofing the `x-shopify-shop-domain` header to name a victim merchant, causing the host application's webhook handler to process attacker-controlled webhook data as if it originated from the victim shop (e.g. triggering data deletion/synchronization logic, disabling the app, or feeding forged order/customer data into per-shop business logic keyed off `WebhookMetadata#shop`). This crosses a tenant boundary using only actions available to any unprivileged internet user who can install the app on a shop they control, which falls under "cross-tenant access."

### Likelihood Explanation
Any user can install a public/dev Shopify app on their own store for free, letting them capture one validly HMAC-signed webhook body/signature pair for a topic the app subscribes to. Replaying it against the app's fixed webhook endpoint with a modified `shop-domain` header requires no credentials, no TLS interception, and no access to `api_secret_key`; the endpoint's URL is fixed by the app (not user-controlled), so no elevated setup is needed beyond a normal app install.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the signed body (e.g., verify the shop domain against an active, previously-established session/webhook-subscription record rather than trusting the header verbatim). At minimum, `Registry.process` should cross-check `request.shop` against the shop associated with the specific `webhook_id`/subscription retrieved from Shopify before dispatching the handler.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger a subscribed webhook topic (e.g. `app/uninstalled`).
2. Capture the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent (both valid, since it's the app's own secret signing the attacker's own event).
3. Replay the exact same body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but change `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) succeeds because it only checks the raw body, and `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches the handler with `shop: "victim.myshopify.com"`, even though Shopify never sent this event for that shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
