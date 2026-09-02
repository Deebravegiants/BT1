### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats an incoming webhook as verified to have "come from Shopify" — including the shop it is attributed to — once `Utils::HmacValidator.validate` passes. In reality, the HMAC signature only covers the raw request body; the `shop-domain`, `topic`, and `webhook-id` headers are excluded from the signed bytes. Because the app's `client_secret` (the HMAC key) is shared across every shop that installs the app, any merchant who can capture one legitimately-signed webhook for their own shop can replay it with the `shop-domain` header changed to a victim shop, and the signature will still validate. This breaks the identity binding between the authenticated bytes (raw body, keyed to the app secret) and the shop identity the gem hands to the app's handler as trustworthy.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 

`hmac` is read straight from the (attacker-controlled) HTTP header, and `to_signable_string` returns only `@raw_body` — none of `topic`, `shop`, `api_version`, or `webhook_id` are included in the signable string: [2](#0-1) 

`Registry.process` validates the HMAC and, if it passes, immediately forwards `request.shop` (the unauthenticated header) to the app's handler as the authoritative tenant identity: [3](#0-2) 

`HmacValidator.validate` only recomputes the signature over `verifiable_query.to_signable_string` (i.e., the raw body) using the app's single, shop-independent `Context.api_secret_key`: [4](#0-3) 

The gem's own documentation asserts a stronger guarantee than what the code provides: it says `Registry.process` "will verify the request did indeed come from Shopify" for the whole request, and explicitly instructs the host app to treat `data.shop` as "The shop domain of the webhook": [5](#0-4) [6](#0-5) 

Because Shopify signs each shop's webhook body using the app's shared `client_secret` (not a per-shop secret), the same HMAC computation succeeds for identical/attacker-replayed bodies regardless of which shop header is attached. The equality the gem is supposed to enforce — "shop attributed to the webhook == shop that produced the signed bytes" — is never checked; only "body bytes == HMAC(body, api_secret_key)" is checked.

### Impact Explanation
Any merchant who has installed the app (an unprivileged action requiring no leaked credentials, tokens, or `api_secret_key`) receives real, validly-signed webhooks for their own shop. They can replay the exact raw body + `hmac-sha256` header to the app's public webhook endpoint while substituting the `shop-domain` (and/or `topic`, `webhook-id`) header for a victim shop. `HmacValidator.validate` still returns `true` because it never inspects those headers, and `Registry.process` dispatches `WebhookMetadata.new(topic:, shop: <victim>, body: <attacker-controlled>, ...)` to the handler as if it were an authentic message from the victim tenant. Any host application that uses `data.shop` to key per-tenant records, trigger per-tenant business logic, or otherwise treat the webhook as originating from that tenant (exactly as the gem's own docs instruct it to) will act on attacker-controlled data labeled with a victim's tenant identity — a cross-tenant boundary violation rooted entirely in this gem's verification logic.

### Likelihood Explanation
Exploitation only requires: (1) the attacker's own instance of the app installed on any shop (public apps are installable by anyone), (2) capturing one legitimate webhook (trivial, since the attacker owns that shop and receives its own webhooks), and (3) sending an HTTP POST to the app's known webhook endpoint with a modified header. No secrets, tokens, or elevated privileges are needed, making this readily reachable by any unprivileged internet user who is a merchant of the target app.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the material that is cryptographically verified, or otherwise independently authenticate the shop header before trusting it:
- Require host applications to cross-check `request.shop` against a known/installed-shop list keyed by an already-authenticated session, rather than presenting it as verified in `WebhookMetadata`.
- Alternatively/additionally, since Shopify does not sign headers, the gem should document explicitly (or enforce) that `shop` on `WebhookMetadata` is unauthenticated and must be corroborated against the app's own installed-shop records before being used for any tenant-scoped action, correcting the current documentation's "verify the request did indeed come from Shopify" claim so it doesn't imply header-level integrity.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and lets Shopify deliver a legitimate webhook, e.g. `orders/create`, capturing:
   - raw body `B`
   - header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's shared `api_secret_key`)
2. Attacker crafts a new HTTP POST to the app's webhook endpoint with:
   - body `B` (unchanged)
   - header `x-shopify-hmac-sha256: H` (unchanged)
   - header `x-shopify-shop-domain: victim-shop.myshopify.com` (changed from `attacker.myshopify.com`)
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` parses fine; `hmac` returns `H`; `to_signable_string` returns `B`.
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(B, api_secret_key)` and matches `H` → validation succeeds (see `lib/shopify_api/utils/hmac_validator.rb` lines 12-31).
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: parsed(B), ...)` (see `lib/shopify_api/webhooks/registry.rb` lines 188-199), even though the data actually originated from `attacker.myshopify.com`.
6. Any handler logic keyed on `data.shop` (as the docs instruct — `docs/usage/webhooks.md` lines 10-17) now processes attacker-controlled order/customer/product data as if it belonged to the victim shop.

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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L123-135)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
