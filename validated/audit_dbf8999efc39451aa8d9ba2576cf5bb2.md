### Title
Webhook HMAC covers only the raw body, not the `shop-domain`/`topic` headers, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator` verifies the HMAC exclusively against that body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values — all of which are read straight from unauthenticated HTTP headers and then handed to the app's webhook handler as trusted identifiers — are never part of the signed material.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

and the `shop`, `topic`, `api_version`, and `webhook_id` accessors simply read from headers without any cryptographic binding to the HMAC: [2](#0-1) 

`HmacValidator.validate` / `validate_signature` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the decoded `hmac` header — i.e., it authenticates the body bytes only: [3](#0-2) 

`Registry.process` relies solely on this body-only HMAC check before dispatching the request to the app's handler using the unauthenticated `shop` and `topic` header values as the tenant/event identity: [4](#0-3) 

The equality the code implicitly assumes is:
`shop-header-used-for-tenant-routing == shop-that-produced-the-signed-body`

but nothing enforces that equality — the HMAC only proves `raw_body` was signed with the app secret; it says nothing about which shop or topic that signature was originally issued for. An attacker who legitimately receives even one genuine `(raw_body, hmac)` pair from Shopify (trivially obtainable by installing the app, free, on the attacker's own store, since Shopify sends real webhooks with valid signatures to any installed app) can replay that exact `raw_body` + `hmac` to the app's single shared webhook endpoint while substituting the `x-shopify-shop-domain` and/or `x-shopify-topic` headers to claim to be a different (victim) shop or a different (e.g. mandatory `app/uninstalled`, `shop/redact`) topic. `Registry.process` will accept it because `Utils::HmacValidator.validate(request)` only checks the body signature, and will hand the forged `shop`/`topic` straight to the app's registered handler via `WebhookMetadata`.

### Impact Explanation
This breaks the tenant isolation boundary the gem is supposed to provide to host apps: the webhook processing API (`Registry.process` + `Request`) is the gem's own surface, and it hands out an unauthenticated shop identity as if it were verified. Any host app that follows the documented pattern of trusting `WebhookMetadata#shop` to decide which tenant's data to update/delete (a standard and expected usage, e.g. processing `app/uninstalled` or `shop/redact` to wipe a shop's stored session/data) can be tricked into acting on behalf of, or against, a different merchant's tenant than the one that actually sent the webhook — a cross-tenant access/integrity issue.

### Likelihood Explanation
Exploitability requires only: (1) the ability to install the target app on any shop the attacker controls (which is the normal, unprivileged way of using a Shopify app) to harvest one genuine `(body, hmac)` pair, and (2) sending an HTTP POST to the app's public webhook endpoint with attacker-chosen headers — no access token, no `api_secret_key`, and no privileged account is required. This is fully reachable through the gem's own `Webhooks::Request` / `Webhooks::Registry` code path.

### Recommendation
Include the `shop-domain`, `topic`, and ideally `webhook-id`/`api-version` values in the signed material verified against the HMAC (or otherwise cryptographically bind them, e.g., by having `to_signable_string` incorporate these header values, matching how `AuthQuery#to_signable_string` binds `shop`/`host`/`code` into its signable string). At minimum, document prominently that `shop`/`topic` in `WebhookMetadata` are unauthenticated and must not be used as sole tenant-routing keys without additional verification (e.g., cross-checking against a known/installed shop list).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and receives a genuine webhook, e.g. body `{}` with header `x-shopify-topic: app/uninstalled`, `x-shopify-shop-domain: attacker.myshopify.com`, and a valid `x-shopify-hmac-sha256` computed by Shopify with the app's real secret over that body.
2. Attacker replays the exact same raw body and `x-shopify-hmac-sha256` value to the app's shared webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `HmacValidator.validate` succeeds because it only checks `HMAC(secret, "{}")`, which is still valid.
4. `Registry.process` dispatches to the registered `app/uninstalled` handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host app to treat `victim.myshopify.com` as having uninstalled the app (e.g., deleting its stored session/data) even though the victim never sent this webhook.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
