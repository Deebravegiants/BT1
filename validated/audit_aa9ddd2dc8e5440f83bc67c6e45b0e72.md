This confirms the analog. The gem's own documentation explicitly states `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" (`docs/usage/webhooks.md:125`), and the resulting `WebhookMetadata.shop` field is documented as "The shop domain of the webhook" that host apps are expected to trust for tenant identification (`docs/usage/webhooks.md:12-14`, `lib/shopify_api/webhooks/webhook_handler.rb:6-12`). However, the HMAC computed by `Utils::HmacValidator.validate` only signs `request.to_signable_string`, which is the raw body — not the `shop-domain` header.

### Title
Webhook HMAC verification does not bind the `shop`/`topic`/`webhook_id` headers, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator.validate` computes/verifies the HMAC solely over that body [1](#0-0) . The `shop`, `topic`, and `webhook_id` values, however, are read directly from unauthenticated HTTP headers [2](#0-1)  and are propagated verbatim into `WebhookMetadata` that the host application's handler is documented to trust for tenant identification [3](#0-2) [4](#0-3) .

### Finding Description
`Registry.process` treats a request as authentic solely based on `Utils::HmacValidator.validate(request)` succeeding: `raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)` [5](#0-4) . The validator checks `OpenSSL.secure_compare(computed_signature, received_signature)` where `computed_signature` is `HMAC(secret, verifiable_query.to_signable_string)` [6](#0-5) . For `Webhooks::Request`, `to_signable_string` is just `@raw_body` [1](#0-0) , meaning the cryptographic proof of authenticity binds *only the body bytes* to the app's secret. The `shop`, `topic`, and `webhook_id` are extracted straight from attacker-controllable HTTP headers with no participation in the signed digest [7](#0-6) .

This breaks the identity binding `HMAC-verified bytes == bytes acted upon`: the equality that should hold is `signed_payload.shop == metadata.shop`, but instead `metadata.shop` is sourced from an entirely separate, unauthenticated channel (the `shopify-shop-domain` header). Any party capable of obtaining one genuine HMAC-signed webhook body/signature pair for a given topic (e.g., a normal merchant who installs the app on their own store and receives an `orders/create` webhook) can replay that exact body+signature to the same webhook endpoint while substituting the `shopify-shop-domain` (and optionally `shopify-topic`/`shopify-webhook-id`) header to claim it originated from a different, victim shop. `Registry.process` will pass HMAC validation (since the body/signature pair is genuinely valid) and dispatch to the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain [8](#0-7) , causing the host application — which the gem's own documentation instructs to key its data storage/queuing off `data.shop` — to attribute the (attacker-controlled) webhook body to the wrong tenant [9](#0-8) .

### Impact Explanation
This is a cross-tenant data-integrity/confusion issue: an app that uses `data.shop` (as the gem's documented example does) to route webhook payloads into per-shop storage or job queues can be made to associate attacker-supplied body content with an arbitrary target shop domain, without needing that shop's credentials. This matches the Critical "cross-tenant access" impact category, since it crosses a tenant boundary using only a body/signature pair the attacker can legitimately obtain for their own shop.

### Likelihood Explanation
Any user who can install the app on a shop they control (a normal, unprivileged onboarding action) can capture a real webhook delivery's raw body and its valid `x-shopify-hmac-sha256` value, then replay it against the app's public webhook endpoint with a forged `shopify-shop-domain` header. No secrets, tokens, or privileged access are required — only the ability to receive one webhook and issue one HTTP replay request.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the data cryptographically bound to the signature, or require `Registry.process`/`WebhookMetadata` to cross-check the `shopify-shop-domain` header against an independently-authenticated source (e.g., a known/expected shop for the given webhook endpoint or session) before trusting it, rather than passing it through directly to the handler.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and registers for `orders/create` webhooks.
2. Shopify delivers a genuine webhook: body `B`, headers including `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's real secret) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays the same request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes HMAC over `B` only, matches `H`, and passes [10](#0-9) .
5. `Registry.process` dispatches to the handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"` even though the body content and signature originated from the attacker's own shop [8](#0-7) .

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

**File:** docs/usage/webhooks.md (L10-16)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L19-30)
```markdown
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-40)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
```
