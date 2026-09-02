## Title
Webhook `shop-domain` / `topic` / `webhook-id` headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, while the shop identity, topic, and webhook id are read from unauthenticated HTTP headers that are never part of the signed message. An attacker who can obtain any single valid `(raw_body, hmac)` pair signed with the app's real secret (trivially available to any unprivileged user who installs the app on their own store and triggers a webhook) can replay that body/HMAC pair while freely rewriting the `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` headers, and the gem will accept it as an authentic webhook for the forged shop/topic.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, and `webhook_id` are pulled from headers that are completely independent of the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` only checks that `hmac` matches `HMAC(secret, to_signable_string)`, i.e. `HMAC(secret, raw_body)`; it never binds the header values into the signature: [3](#0-2) 

`Registry.process` uses exactly this validation, then trusts `request.shop`, `request.topic`, and `request.webhook_id` unconditionally when dispatching to the registered handler: [4](#0-3) 

The identity binding that should hold is:
`HMAC_valid(raw_body) == true` should imply `(shop, topic, webhook_id)` are authentic for that body.

In reality the equality that holds is only:
`HMAC(secret, raw_body) == hmac` — with `shop`, `topic`, `webhook_id` completely uncorrelated to that check.

Because any app installed on any store (including one an attacker fully controls) receives real webhooks signed by Shopify with the app's genuine shared secret, an attacker can:
1. Install the target public app on their own (attacker-controlled) shop.
2. Trigger a webhook whose body content they control/observe (e.g., `orders/create`, or one of the mandatory GDPR topics `shop/redact`, `customers/redact`, `customers/data_request`), capturing the legitimate `(raw_body, X-Shopify-Hmac-Sha256)` pair. [5](#0-4) 
3. Replay this exact `raw_body` + `hmac` to the app's public webhook endpoint, but with the `x-shopify-shop-domain` header rewritten to a **victim** shop, and/or the `x-shopify-topic` header rewritten to a topic the attacker wants to trigger (e.g. `shop/redact`).
4. `HmacValidator.validate` still succeeds (it never inspected the headers), so `Registry.process` calls the registered handler with `WebhookMetadata` claiming the forged shop/topic: [6](#0-5) 

The handler then acts on attacker-controlled `body` content believing it is authentic data for the victim shop — this is a direct cross-tenant identity confusion vulnerability rooted entirely inside this gem's webhook verification code, not in host-application misuse.

### Impact Explanation
This breaks the shop-identity binding for webhooks, allowing an attacker to make the host application process attacker-chosen webhook payloads under an arbitrary victim shop's identity, or trigger arbitrary registered topics (including mandatory data-erasure topics like `shop/redact`/`customers/redact`) against a victim tenant. This is a cross-tenant confusion vulnerability caused entirely by a gap between what is HMAC-verified (`raw_body` only) and what is trusted/acted upon (`shop`, `topic`, `webhook_id` headers), matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any unprivileged internet user can become an "unprivileged" attacker here simply by installing the target public app on a free/dev store they control, which is the normal minimum bar to obtain a valid signed webhook. No access token, `client_secret`, or privileged account is required — only a genuine webhook delivery from Shopify to the attacker's own store, which the app owner cannot prevent.

### Recommendation
Include the header-derived identity fields (`shop-domain`, `topic`, `webhook-id`) in the signed material verified for each webhook, or otherwise cryptographically bind them to the raw body (e.g., derive/validate shop identity from a value embedded in the signed payload, or require out-of-band confirmation that the shop belongs to a session known to have installed the app for that topic) before dispatching to `handler.handle`. At minimum, `Webhooks::Request#to_signable_string` should not silently ignore header fields that downstream code treats as authenticated.

### Proof of Concept
1. Install the target app (any public Shopify app using this gem) on attacker-owned shop `attacker-shop.myshopify.com`.
2. Trigger a webhook for a registered topic; capture `raw_body` and the `X-Shopify-Hmac-Sha256` header from the real Shopify-signed delivery.
3. Send a forged HTTP POST directly to the app's webhook receiver endpoint with:
   - Body: the captured `raw_body` (unchanged)
   - Header `X-Shopify-Hmac-Sha256`: unchanged (still valid, since it only signs the body)
   - Header `X-Shopify-Shop-Domain`: `victim-shop.myshopify.com`
   - Header `X-Shopify-Topic`: e.g. `shop/redact` or any topic registered by the app
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which returns `true` because only `raw_body` is checked. The registered handler for the forged topic is invoked with `WebhookMetadata` reporting `shop: "victim-shop.myshopify.com"`, even though that data never originated from Shopify for that shop. [4](#0-3)

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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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
