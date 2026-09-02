This confirms the design and impact clearly enough to report.

### Title
Webhook shop-domain header is not covered by HMAC, allowing shop-identity spoofing in `ShopifyAPI::Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The gem verifies webhook authenticity by computing an HMAC over the raw request body only. The `shop` (and `topic`/`webhook_id`/`api_version`) values that the host application actually acts on are taken from HTTP headers that are never included in the signed content, so a request with a valid HMAC for one shop's payload can be relabeled as belonging to a different shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [1](#0-0) 
`Utils::HmacValidator.validate` verifies only `verifiable_query.to_signable_string` (the body) against the HMAC secret: [2](#0-1) 
`Webhooks::Registry.process` validates that HMAC and then hands the (unverified) `request.shop` straight to the app's handler as trusted identity: [3](#0-2) 

This breaks the intended binding `HMAC(body) == HMAC(body)` ⇒ `shop is authentic`. In reality the HMAC only proves the *body* bytes are authentic for *some* shop that shares the app's `client_secret` (i.e., any shop that has installed the app), it says nothing about which shop the body belongs to. The documentation explicitly tells host apps to trust `data.shop` as the webhook's shop identity for downstream processing (e.g., looking up per-shop sessions/tokens) with no additional verification expected of the caller: [4](#0-3) , and `docs/usage/webhooks.md` line 125 states processing "will verify the request did indeed come from Shopify" — implying the shop attribution is trusted once HMAC passes.

### Impact Explanation
Any unprivileged actor who can install the public app on their own store (a normal, unprivileged action requiring no stolen credentials) receives legitimate webhook deliveries for their own shop with a correctly computed HMAC over the body. Because the header carrying the shop domain is outside the signed content, the attacker can replay that valid `(body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with an arbitrary victim shop domain. `Registry.process` will accept the HMAC as valid and invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain. Host applications commonly use this `shop` value to look up the victim's stored session/access token and perform shop-scoped side effects (sync, refunds, deletion, `app/uninstalled` cleanup, etc.), so this enables cross-tenant impact: an attacker-controlled body is processed under a victim shop's identity/session.

### Likelihood Explanation
Exploitation requires only the ability to install the target app on any store (including a free/development store) and the ability to POST an HTTP request with attacker-controlled headers to the app's known webhook endpoint — no `api_secret_key`, access token, or `client_secret` is needed. This is realistic for any public/multi-tenant Shopify app that uses this gem's webhook processing as documented.

### Recommendation
Bind the identity fields used for authorization/routing to the HMAC-verified content: include `shop`, `topic`, and `webhook_id` in the signable string (or otherwise cryptographically bind them, e.g. re-deriving/confirming shop from a value covered by the signature or from a previously established, verified per-installation secret) before trusting `request.shop` in `Webhooks::Registry.process`.

### Proof of Concept
1. Attacker installs the target app on their own dev store `attacker-shop.myshopify.com`, subscribing to `orders/create`.
2. Shopify delivers a legitimate webhook to the attacker's registered callback with body `B` and header `x-shopify-hmac-sha256` = `HMAC(client_secret, B)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, HMAC)` and sends a forged POST to the app's real webhook endpoint with the same body `B` and same HMAC header, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds (only checks body vs HMAC): [5](#0-4) 
5. `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"` and attacker-controlled body `B`, causing the host application to perform victim-shop-scoped processing using attacker data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
```
